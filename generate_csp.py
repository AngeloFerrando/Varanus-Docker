import sys
import string

def generate_characters(size):
    if size <= 0:
        return []
    
    # Generate the base list of single characters
    alphabet = list(string.ascii_lowercase)
    result = alphabet[:size]
    
    # If size is more than 26, start generating combinations
    if size > 26:
        extra_chars = []
        i = 0
        while len(result) < size:
            for char in alphabet:
                extra_chars.append(alphabet[i] + char)
                if len(result) + len(extra_chars) >= size:
                    result.extend(extra_chars[:size - len(result)])
                    return result
            i += 1
            result.extend(extra_chars)
            extra_chars = []

    return result

def generate_csp(N):
    events = generate_characters(N)
    processes = [f"Proc{ev}" for ev in events]

    # Header
    csp_content = f"-- Automatically building a Worst-Case State Machine (WCST)\n-- Now with {N} events and {N} states\n"
    
    # Channels
    csp_content += "channel " + ", ".join(events) + "\n\n"

    # Processes
    for process in processes:
        csp_content += f"{process} =\n"
        for i, event in enumerate(events):
            csp_content += f"{event} -> {process}\n" if i == 0 else f"[]\n{event} -> {processes[i]}\n"
        csp_content += "\n"
    
    # Main process
    csp_content += f"WCST = {processes[0]} -- Main Process, starts the recursion in {processes[0]}\n\n"

    # Assertions
    csp_content += "assert WCST; RUN(Events) :[deadlock free]:\n"
    csp_content += "assert WCST :[deterministic]:\n"
    csp_content += "assert WCST :[divergence free]:\n"

    return csp_content


if __name__ == "__main__":
    N = int(sys.argv[1])
    csp_file_content = generate_csp(N)
    with open("wcst.csp", "w") as file:
        file.write(csp_file_content)
    print("CSP file generated as wcst.csp")
