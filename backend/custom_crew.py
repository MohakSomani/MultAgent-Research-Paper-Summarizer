from typing import List, Dict, Callable
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class CustomAgent:
    def __init__(self, role: str, goal: str, backstory: str, tools: List[Callable], 
                 llm: LlamaCpp, verbose: bool = True):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        # Handle tools that may not have a __name__ attribute
        self.tools = {getattr(tool, "__name__", str(tool)): tool for tool in tools}
        self.llm = llm
        self.verbose = verbose
        
    def execute_task(self, task_description: str, context: str = "") -> str:
        prompt = PromptTemplate(
            input_variables=["context", "task", "role", "goal", "backstory"],
            template="""[ROLE] {role}
[GOAL] {goal}
[BACKSTORY] {backstory}
[CONTEXT] {context}
[TASK] {task}
Response:"""
        )
        
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            verbose=True  # Enable verbose logging
        )
        
        print(f"Executing task with prompt:\n{prompt.format(context=context, task=task_description, role=self.role, goal=self.goal, backstory=self.backstory)}")
        return chain.run({
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "context": context,
            "task": task_description
        })

class CustomTask:
    def __init__(self, description: str, expected_output: str, agent: CustomAgent, 
                 tools: List[str], context: List[str] = None):
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
        self.tools = tools
        self.context = context or []
        
    def execute(self, inputs: Dict) -> str:
        context = "\n".join(self.context)
        task_input = self.description.format(**inputs)
        
        # Use tools if specified
        for tool_name in self.tools:
            if tool_name in self.agent.tools:
                tool_result = self.agent.tools[tool_name](inputs)
                context += f"\nTool {tool_name} output: {tool_result}"
        
        return self.agent.execute_task(
            task_description=task_input,
            context=context
        )

class CustomCrew:
    def __init__(self, tasks: List[CustomTask], agents: List[CustomAgent], 
                 process: str = "sequential", verbose: bool = True):
        self.tasks = tasks
        self.agents = agents
        self.process = process
        self.verbose = verbose
        
    def kickoff(self, inputs: Dict = None) -> Dict:
        results = {}
        context = []
        
        for task in self.tasks:
            if self.verbose:
                print(f"Executing task: {task.description}")
                
            result = task.execute(inputs)
            results[task.description] = result
            context.append(result)
            
            if self.verbose:
                print(f"Task result: {result[:200]}...")
                
        return results
