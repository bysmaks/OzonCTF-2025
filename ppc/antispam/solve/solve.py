import grpc
import torch
from classificator_pb2 import Nothing, Token, SubmitSampleRequest
from classificator_pb2_grpc import ClassificatorStub
from transformers import pipeline, RobertaTokenizer, RobertaForSequenceClassification

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
classifier = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment", device=0 if torch.cuda.is_available() else -1)

tokenizer = RobertaTokenizer.from_pretrained("mshenoda/roberta-spam")
model = RobertaForSequenceClassification.from_pretrained("mshenoda/roberta-spam").to(device)

channel = grpc.insecure_channel('ppc.ozon-ctf-2025.ru:50051')
stub = ClassificatorStub(channel)

def predict_spam(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    return "Spam" if torch.argmax(outputs.logits, dim=1).item() == 1 else "Ham"

def classify_text(comment):
    if predict_spam(comment[:512]) == "Spam":
        return SubmitSampleRequest.SPAM
    score = int(classifier(comment[:512])[0]['label'].split()[0])
    return SubmitSampleRequest.POSITIVE if score >= 4 else SubmitSampleRequest.NEGATIVE

token = stub.Register(Nothing())

for i in range(1000):
    sample = stub.GetSample(token)
    stub.SubmitSample(SubmitSampleRequest(token=token, uid=sample.uid, probable_class=classify_text(sample.comment)))
    print(f"Sample {i} submitted successfully")

print(f"Flag result: {stub.GetFlag(token).message}")
