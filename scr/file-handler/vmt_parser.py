import logging

def parse_vmt_file(filepath):
    parameters = {}
    try:
        with open(filepath, "r") as file:
            lines = file.readlines()

        shader_line = lines[0].strip().lower()
        parameters["shader"] = shader_line if shader_line in ["vertexlitgeneric", "lightmappedgeneric", "unlitgeneric", "lightmappedreflective"] else "unknown"

        current_context = parameters
        context_stack = []

        for line in lines[1:]:
            line = line.strip()
            if line.startswith('//') or not line:
                continue
            if line.startswith('{'):
                context_stack.append(current_context)
                current_context = {}
                continue
            if line.startswith('}'):
                previous_context = context_stack.pop()
                previous_context.update(current_context)
                current_context = previous_context
                continue

            if ' ' not in line:
                current_context[line] = {}
                continue

            key, val = line.split(None, 1)
            key = key.strip('"').lower()
            val = val.split('//')[0].strip().strip('"')
            current_context[key] = val

        logging.info(f"Parsed VMT file '{filepath}': {parameters}")

    except Exception as e:
        logging.error(f"Unable to open or parse {filepath}: {e}")
        parameters["ERROR"] = f"Unable to open or parse {filepath}: {e}"
    return parameters
