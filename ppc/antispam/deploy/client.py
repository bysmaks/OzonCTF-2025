import grpc
from target.pypro.classificator_pb2 import Nothing, Token, SubmitSampleRequest
from target.pypro.classificator_pb2_grpc import ClassificatorStub

def run():
    # Create a secure channel to the server
    channel = grpc.insecure_channel('localhost:50051')
    stub = ClassificatorStub(channel)

    try:
        # Register and get token
        token = stub.Register(Nothing())
        print(f"Received token: {token.token}")

        # Get flag
        flag_result = stub.GetFlag(token)
        print(f"Flag result: {flag_result.message}")

        while True:
            # Get a sample
            sample = stub.GetSample(token)
            print(f"Received sample - UID: {sample.uid}, Comment: {sample.comment}")

            probable_class = input("class> ")
            if probable_class == "neg":
                probable_class = SubmitSampleRequest.NEGATIVE
            elif probable_class == "pos":
                probable_class = SubmitSampleRequest.POSITIVE
            elif probable_class == "spam":
                probable_class = SubmitSampleRequest.SPAM

            # Submit classification for the sample
            submit_request = SubmitSampleRequest(
                token=token,
                uid=sample.uid,
                probable_class=probable_class  # Can be NEGATIVE, POSITIVE, or SPAM
            )
            stub.SubmitSample(submit_request)
            print("Sample submitted successfully")

            # Get flag
            flag_result = stub.GetFlag(token)
            print(f"Flag result: {flag_result.message}")

    except grpc.RpcError as e:
        print(f"RPC failed: {e}")

if __name__ == '__main__':
    run()