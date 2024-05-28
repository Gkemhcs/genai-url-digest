from flask import Flask ,request,jsonify
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_postgres.vectorstores import PGVector 
#from langchain_community.vectorstores.pgvector import PGVector
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai import VertexAI

connection = "postgresql+psycopg://gkem:gkem123@localhost:5432/urldigest"
llm=VertexAI()
embeddings=VertexAIEmbeddings(model_name="textembedding-gecko")


app=Flask(__name__)

@app.route("/")
def home():
       return {"status":200,"message":"everything is working fine"}

@app.route("/process_url",methods=["POST"])
def process():
         print("hello request")
         
         urls=request.form.getlist("urls")
         print(urls)
         loader = UnstructuredURLLoader(urls=urls)
         data = loader.load()
         text_splitter = RecursiveCharacterTextSplitter(
         separators=['\n\n', '\n', '.', ','],
         chunk_size=1000
         )
         docs = text_splitter.split_documents(data)
       
         
         print(docs[0])
         vectorstore = PGVector(
         embeddings=embeddings,
         collection_name=request.form.get("username"),
         connection=connection,
         use_jsonb=True,
          )
         db=vectorstore.add_documents(docs)
         print("db",db)
         return {"status":"ok"}
@app.route("/ask_question", methods=["POST"])
def ask_question():
    
        question = request.form.get("question")
        print(question)
        if not question:
            return jsonify({"status": 400, "message": "No question provided"}), 400

        # Initialize PGVector for vector search
        vectorstore = PGVector(
            embeddings=embeddings,
            collection_name=request.form.get("username"),
            connection=connection,
            use_jsonb=True,
        )
        chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorstore.as_retriever())
        # Perform vector search
        result = chain({"question": question}, return_only_outputs=True)
        
        # Format the results
       
        sources = result.get("sources", "")
        
        if sources:
          return jsonify({"status": 200, "answer": result["answer"],"sources":sources})
   
        print(result["answer"])
        return jsonify({"status": 200, "answer": result["answer"]})

if(__name__=="__main__"):
       app.run(port=5001,host="0.0.0.0")



