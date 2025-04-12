from crewai import Crew
from tasks import search_task, summarize_task, podcast_task

def main():
    crew = Crew(
        tasks=[search_task(), summarize_task(), podcast_task()],
        verbose=2
    )
    
    result = crew.kickoff()
    print(f"Final result:\n{result}")

if __name__ == "__main__":
    main()