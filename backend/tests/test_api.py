from backend.rag.retriever import search

results = search("What does Tate say about God?", top_k=3)
for text, video_id in results:
    print(f"From video {video_id}:")
    print(text)
    print("-" * 50)
