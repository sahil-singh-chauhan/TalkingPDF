from langchain.prompts import PromptTemplate, ChatPromptTemplate

query_prompt = PromptTemplate(
    input_variables=["question"],
    template="""You are an AI language model assistant, your task is to generate
    five different versions of the given user question to retrieve relevant documents
    from a vector database. Provide these alternative questions separated by new lines.
    Original question: {question}"""
)

chat_prompt_template = """Answer the question based only on the following context:
{context}

Question: {question}
"""

chat_prompt = ChatPromptTemplate.from_template(chat_prompt_template)
