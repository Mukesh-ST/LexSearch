import os
import json
from dotenv import load_dotenv
from groq import Groq
from ingestor import ingest_documents
from pipeline import process_query

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TEST_QUESTIONS = [
    "What is the time limit to respond to an RTI request?",
    "Who is a Public Information Officer?",
    "What are the penalties for hacking under IT Act 2000?",
    "Can RTI be rejected? What are the grounds?",
    "What is the appeal process under RTI Act?",
    "What are the exemptions under RTI Act?",
    "What is the penalty for unauthorized access under IT Act?",
    "What is the role of Central Information Commission?",
    "What is cybercrime under IT Act 2000?",
    "What happens if a PIO fails to respond to RTI?",
]

GROUND_TRUTHS = [
    "The time limit to respond to an RTI request is 30 days. For life or liberty matters, it is 48 hours.",
    "A Public Information Officer is an officer designated by public authorities to provide information under RTI Act.",
    "Under Section 66 of IT Act 2000, hacking is punishable with imprisonment up to 3 years or fine up to 2 lakh rupees.",
    "Yes, RTI can be rejected under Sections 8 and 9 on grounds like national security, personal information, and cabinet papers.",
    "First appeal goes to a senior officer within 30 days. Second appeal goes to Information Commission within 90 days.",
    "Exemptions under Section 8 include national security, trade secrets, personal privacy, cabinet notes and ongoing investigations.",
    "Section 43 provides compensation up to 1 crore for unauthorized access. Section 66 provides criminal penalty.",
    "Central Information Commission hears second appeals and complaints under RTI Act and can impose penalties on PIOs.",
    "Cybercrime under IT Act includes unauthorized access, hacking, data theft, identity fraud, and publishing obscene material.",
    "If PIO fails to respond within 30 days, applicant can file first appeal and PIO may face penalty of Rs 250 per day up to Rs 25000.",
]


def evaluate_answer(question, answer, context, ground_truth):
    """Use Groq to evaluate faithfulness and relevancy"""
    prompt = f"""You are an evaluation judge. Score the following answer on 3 metrics.
Return ONLY a JSON object with scores between 0 and 1.

Question: {question}
Ground Truth: {ground_truth}
Retrieved Context: {context[:500]}
Generated Answer: {answer[:500]}

Score these metrics:
- faithfulness: Is the answer grounded in the retrieved context? (0-1)
- answer_relevancy: Does the answer address the question? (0-1)  
- context_precision: Is the context relevant to the question? (0-1)

Return only this JSON format, nothing else:
{{"faithfulness": 0.0, "answer_relevancy": 0.0, "context_precision": 0.0}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=100
    )
    
    raw = response.choices[0].message.content.strip()
    try:
        scores = json.loads(raw)
    except:
        # fallback if JSON parsing fails
        scores = {"faithfulness": 0.5, "answer_relevancy": 0.5, "context_precision": 0.5}
    return scores


def run_evaluation():
    print("=== LexSearch Custom Evaluation ===\n")
    
    chunks = ingest_documents("./resources")
    
    all_scores = []
    
    for i, (question, ground_truth) in enumerate(zip(TEST_QUESTIONS, GROUND_TRUTHS)):
        print(f"Q{i+1}: {question}")
        try:
            result = process_query(question, chunks, top_k=5)
            answer = result["answer"]
            context = " ".join([
                chunk["chunk"]["parent_text"]
                for chunk in result["context_chunks"][:2]
            ])
            
            scores = evaluate_answer(question, answer, context, ground_truth)
            all_scores.append(scores)
            print(f"  Faithfulness: {scores['faithfulness']:.2f} | "
                  f"Relevancy: {scores['answer_relevancy']:.2f} | "
                  f"Precision: {scores['context_precision']:.2f}\n")
        except Exception as e:
            print(f"  Error: {e}\n")

    # Aggregate scores
    if all_scores:
        avg_faithfulness = sum(s["faithfulness"] for s in all_scores) / len(all_scores)
        avg_relevancy = sum(s["answer_relevancy"] for s in all_scores) / len(all_scores)
        avg_precision = sum(s["context_precision"] for s in all_scores) / len(all_scores)
        overall = (avg_faithfulness + avg_relevancy + avg_precision) / 3

        print("=== Final Evaluation Results ===")
        print(f"Faithfulness:      {avg_faithfulness:.4f}")
        print(f"Answer Relevancy:  {avg_relevancy:.4f}")
        print(f"Context Precision: {avg_precision:.4f}")
        print(f"Overall Score:     {overall:.4f}")

        # Save results
        with open("evaluation_results.txt", "w") as f:
            f.write("=== LexSearch Evaluation Results ===\n\n")
            f.write(f"Total questions evaluated: {len(all_scores)}\n\n")
            f.write(f"Faithfulness:      {avg_faithfulness:.4f}\n")
            f.write(f"Answer Relevancy:  {avg_relevancy:.4f}\n")
            f.write(f"Context Precision: {avg_precision:.4f}\n")
            f.write(f"Overall Score:     {overall:.4f}\n")

        print("\nResults saved to evaluation_results.txt")


if __name__ == "__main__":
    run_evaluation()