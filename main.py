from agent.agentGraph import agentGraph

def main():
    user_prompt = "Develop a calculator app in html"
    state = {"user_prompt": user_prompt, "recursion_limit": 50}
    

    result = agentGraph.invoke(state)



if __name__ == "__main__":
    main()
