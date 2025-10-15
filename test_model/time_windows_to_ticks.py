def generate_time_windows(llm: Llm, ump: Ump) -> List[TimeWindow]:
    time_windows=[]
    scope_start = 0
    scope_end = llm.scope_end
    
    
    
