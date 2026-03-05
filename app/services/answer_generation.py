from transformers import pipeline

# Initializing with 'text-generation' for better stability in this environment
# This resolves the KeyError: 'Unknown task text2text-generation'
qa_pipeline = pipeline("text-generation", model="google/flan-t5-base")

def generate_answer(question, context_chunks):
    if not context_chunks:
        return "I could not find this in the provided documents."

    context_text = "\n\n".join([c["chunk_text"] for c in context_chunks])
    
    # Strict prompt to ensure the output is just a clean paragraph
    prompt = f"Answer the following question in one short paragraph using only the context.\nContext: {context_text}\nQuestion: {question}\nAnswer:"

    # Generate the response
    response = qa_pipeline(prompt, max_length=150, do_sample=False)
    
    # Extract only the text generated after the word 'Answer:'
    full_text = response[0]['generated_text']
    answer = full_text.split("Answer:")[-1].strip()
    return answer