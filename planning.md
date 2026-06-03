# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
My domain is an unofficial student guide to social life around Mississippi State University, specifically focusing on the best local bars, parks, and spots to meet people in Starkville. This student-generated knowledge is highly valuable for incoming students trying to navigate the local culture. However, it is hard to find through official channels because the official MSU website focuses strictly on university academics and campus operations, leaving out the real student perspective on off-campus nightlife, hangouts, and recreational spots.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | r/Msstate Subreddit | Thread breaking down local Starkville bar atmospheres and crowds. | https://www.reddit.com/r/Msstate/comments/debuvp/starkville_bars/ |
| 2 | r/Msstate Subreddit | Student recommendations on the best bars for visitors and weekend nightlife. | https://www.reddit.com/r/Msstate/comments/1bc9gc5/best_bars_for_visitors/ |
| 3 | r/Msstate Subreddit | Community discussion on the best outdoor hiking trails and nature areas around town. | https://www.reddit.com/r/Msstate/comments/ew77dk/good_places_around_starkville_to_hike/ |
| 4 | r/Msstate Subreddit | Student debate regarding the best scenic outdoor date and hangout spots in Starkville. | https://www.reddit.com/r/Msstate/comments/179p3b/the_lovers_guide_to_starkville_best_places_to/ |
| 5 | Yelp Reviews | Student opinions and crowd feedback on Dave's Dark Horse Tavern's dive bar vibe. | https://www.yelp.com/biz/daves-dark-horse-tavern-starkville |
| 6 | TripAdvisor Reviews | Visitor and student feedback highlighting trail conditions at Noxubee National Wildlife Refuge. | https://www.tripadvisor.com/Attraction_Review-g43999-d269865-Reviews-Noxubee_National_Wildlife_Refuge-Starkville_Mississippi.html |
| 7 | Yelp Reviews | Local reviews on Rick's Cafe, detailing its live music scene, concerts, and crowds. | https://www.yelp.com/biz/ricks-cafe-starkville |
| 8 | Yelp Reviews | Community feedback on 929 Coffee Bar's environment for studying and meeting people. | https://www.yelp.com/biz/929-coffee-bar-starkville |
| 9 | Yelp Reviews | Reviews focusing on the student-heavy dining atmosphere at Two Brothers Smoked Meats in the Cotton District. | https://www.yelp.com/biz/two-brothers-smoked-meats-starkville |
| 10 | TripAdvisor Reviews | Reviews detailing recreational amenities, walking tracks, and picnic spots at McKee Park. | https://www.tripadvisor.com/Attraction_Review-g43999-d10291931-Reviews-McKee_Park-Starkville_Mississippi.html |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 500 Character

**Overlap:** 50 character

**Reasoning:** The documents consist of short Reddit comments, casual forum threads, and local reviews about Starkville social spots. A 500-character chunk size ensures we capture complete recommendations (e.g., a specific bar's atmosphere or a park's location) without mixing multiple unrelated reviews together. The 50-character overlap prevents critical context—like the name of the establishment being mentioned at the very end of a sentence—from being lost across chunk boundaries.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 (via sentence-transformers)

**Top-k:** 4

**Production tradeoff reflection:** If deploying this for thousands of real MSU students, I would prioritize a balance between low latency and high relevance. A massive, state-of-the-art embedding model might be slightly more accurate, but if it takes 10 seconds to load on a phone, students won't use it. I would weigh the latency of calling an external API versus running a smaller, faster model locally to ensure the search feels instant and relevant.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What is the overall vibe and student crowd like at Dave's Dark Horse Tavern compared to Rick's Cafe? | Chunks from Yelp should show Dave's is a relaxed dive bar with pizza/live music, while Rick's is a high-energy concert venue. |
| 2 | What do students recommend bringing or doing when visiting the Noxubee National Wildlife Refuge? | Chunks from TripAdvisor should mention specific trails, boardwalks, wildlife watching, or gear like bug spray. |
| 3 | Is 929 Coffee Bar considered a good spot for quiet studying, or is it more of a loud social hangout? | Chunks from Yelp should discuss the ambient noise level, seating availability, and student habits during study hours. |
| 4 | What are the top recommended food items and atmosphere highlights mentioned for Two Brothers Smoked Meats in the Cotton District? | Chunks from Yelp should highlight student favorite dishes (like smoked wings) and the outdoor/balcony patio vibe. |
| 5 | What are the primary recreational features available for students at McKee Park? | Chunks from TripAdvisor should detail specific amenities like walking tracks, tennis courts, or pavilion spaces. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Filtering by Relevance and Popularity:** Reddit threads and Yelp pages contain a mix of highly upvoted, trusted recommendations and low-quality comments with few upvotes or no replies. Our system risks retrieving unpopular or irrelevant opinions if we don't account for these popularity signals during ingestion.
2. **Structural Text Noise:** Raw data from different platforms includes layout clutter like usernames, timestamps, upvote counts, and HTML tags. This non-narrative text can disrupt chunking boundaries and dilute the semantic meaning of the actual reviews.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---
[Documents: Reddit/Yelp] ──> (Ingestion & Cleaning) ──> (Chunking: 500 chars)
                                                                │
[Gradio UI] <── (LLM Generation) <── (Retrieval: Top-4) <── [ChromaDB Store]

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->
**Milestone 3 — Ingestion and chunking:**
* **AI Tool:** Gemini or Claude chat.
* **Input:** I will provide the AI with my **Domain** summary, the **Chunking Strategy** (500 characters, 50-character overlap), and a sample of raw text from my sources. 
* **Expected Output:** A Python script utilizing a library like `LangChain` or basic string manipulation to clean text (removing HTML/clutter) and split it into properly sized chunks.
* **Verification:** I will print the length and content of the first 3 chunks in my terminal to verify they match the 500-character size and 50-character overlap requirements.

**Milestone 4 — Embedding and retrieval:**
* **AI Tool:** Gemini or Claude chat.
* **Input:** I will provide my **Retrieval Approach** specs (`all-MiniLM-L6-v2` embedding model and `top-k=4`) and ask it to write code to initialize a local vector database.
* **Expected Output:** Python code using `sentence-transformers` and `ChromaDB` to embed the text chunks, store them, and write a query function that returns the top 4 most relevant chunks.
* **Verification:** I will test a query like "Dave's Dark Horse Tavern" and print out the source URLs of the top 4 retrieved chunks to make sure they are actually about Dave's.

**Milestone 5 — Generation and interface:**
* **AI Tool:** Gemini or Claude chat.
* **Input:** I will provide the **Evaluation Plan** questions, my architecture layout, and instructions for connecting to the Groq API using `llama-3.3-70b-versatile`.
* **Expected Output:** A Python script that injects the 4 retrieved chunks into an LLM system prompt ("Answer using only the provided text") and a simple `Gradio` web interface script.
* **Verification:** I will run my 5 evaluation questions through the interface and check if the model accurately answers them and strictly cites its sources without hallucinating.
