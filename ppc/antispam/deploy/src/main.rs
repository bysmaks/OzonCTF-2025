use std::sync::LazyLock;
use classificator::{classificator_server::{Classificator, ClassificatorServer}, FlagResult, Nothing, Sample, SubmitSampleRequest, Token};
use csv::StringRecord;
use rand::distr::{Alphanumeric, SampleString as _};
use tonic::{transport::Server, Request, Response, Status};
use anyhow::Result;
use redis::AsyncCommands as _;
use rand::prelude::*;

pub mod classificator {
    tonic::include_proto!("classificator");
}

fn generate_token() -> String {
    Alphanumeric.sample_string(&mut rand::rng(), 32)
}

static DATASET: LazyLock<Vec<StringRecord>> = LazyLock::new(|| {
    csv::Reader::from_reader(&include_bytes!("dataset.csv")[..])
        .records()
        .map(|e| e.expect("Error reading the dataset."))
        .collect()
});

#[derive(Debug)]
pub struct ClassificatorImpl {
    pub redis_conn: redis::aio::MultiplexedConnection,
}

#[tonic::async_trait]
impl Classificator for ClassificatorImpl {
    async fn register(
        &self,
        _: Request<Nothing>,
    ) -> Result<Response<Token>, Status> {
        let token = generate_token();
        self.redis_conn.clone().set::<String, i64, ()>(format!("{token}:overall"), 0).await
            .map_err(|e| {
                println!("{e}");
                Status::internal("Internal server error")
            })?;
        self.redis_conn.clone().set::<String, i64, ()>(format!("{token}:right"), 0).await
            .map_err(|e| {
                println!("{e}");
                Status::internal("Internal server error")
            })?;
        Ok(Response::new(Token { token }))
    }

    async fn get_sample(
        &self,
        request: Request<Token>,
    ) -> Result<Response<Sample>, Status> {
        let Token { token } = request.into_inner();
        let record = DATASET.choose(&mut rand::rng()).unwrap();
        let (content, class) = record.deserialize(None).expect("Dataset is broken.");
        let record_uid = generate_token();
        self.redis_conn.clone().set::<String, u8, ()>(format!("{token}:{record_uid}"), class).await
            .map_err(|e| {
                println!("{e}");
                Status::internal("Internal server error")
            })?;
        Ok(Response::new(Sample { uid: record_uid, comment: content }))
    }

    async fn submit_sample(
        &self,
        request: Request<SubmitSampleRequest>,
    ) -> Result<Response<Nothing>, Status> {
        let SubmitSampleRequest { token, uid, probable_class } = request.into_inner();
        let Token { token } = token
            .ok_or_else(|| Status::invalid_argument("Token missing"))?;
        let answer = self.redis_conn.clone().get_del(format!("{token}:{uid}")).await
            .map_err(|e| {
                println!("{e}");
                Status::internal("Internal server error")
            })?;
        self.redis_conn.clone().incr::<String, i64, ()>(format!("{token}:overall"), 1).await
            .map_err(|e| {
                println!("{e}");
                Status::internal("Internal server error")
            })?;
        if probable_class == answer {
            self.redis_conn.clone().incr::<String, i64, ()>(format!("{token}:right"), 1).await
                .map_err(|e| {
                    println!("{e}");
                    Status::internal("Internal server error")
                })?;
        }
        Ok(Response::new(Nothing{}))
    }

    async fn get_flag(
        &self,
        request: Request<Token>,
    ) -> Result<Response<FlagResult>, Status> {
        let Token { token } = request.into_inner();
        let overall = self.redis_conn.clone().get::<String, i64>(format!("{token}:overall")).await
            .map_err(|e| {
                println!("{e}");
                Status::internal("Internal server error")
            })?;
        let right = self.redis_conn.clone().get::<String, i64>(format!("{token}:right")).await
            .map_err(|e| {
                println!("{e}");
                Status::internal("Internal server error")
            })?;
        if overall >= 1000 && right as f64 / overall as f64 > 0.63 {
            Ok(Response::new(FlagResult {
                message: std::env::var("FLAG")
                    .map_err(|e| {
                        println!("Can't get FLAG: {e}");
                        Status::internal("Internal server error")
                    })?
            }))
        } else {
            Ok(Response::new(FlagResult {
                message: format!("You are not trustworthy enough (categorize at least 1000 entries reliably)")
            }))
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "0.0.0.0:50051".parse()?;
    let greeter = ClassificatorImpl {
        redis_conn: redis::Client::open(std::env::var("REDIS_URL")?)?
                                    .get_multiplexed_async_connection().await?
    };

    println!("fdfsf");

    Server::builder()
        .add_service(ClassificatorServer::new(greeter))
        .serve(addr)
        .await?;

    Ok(())
}
