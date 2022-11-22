from traceback import print_exc

ERROR_PREFIX = "[ERROR]"
WARN_PREFIX = "[WARN]"
VARIABLE_GETTER_PREFIX = "$"
INFORM_VARIABLE_GETTING = True # Wethet the console should print when variables get replaced by their value int commands

enabled: bool = False # Is the Main Loop active ? /!\ To start the main loop, use start_loop() instead)

start_prompt: str = "Enter a command : " # The message shown by input() at the start of an iteration (indicate to the user that he can type a command)
end_prompt: str = "" # The string printed at the end of the iteration (), empty for no prompt
command_error_prompt: str = f"{ERROR_PREFIX} Unrecognised command : `%s`"

commands: "list[Command]" = [] # The array containing all commands objects (defaults : SET_VARIABLE_COMMAND)
stop_cmd: str = "stop" # The command's string wich stop the loop

pre_funcs: list[callable] = [] # Functions called at the start of the iteration
input_funcs: list[callable] = [str.lower] # Functions called after each input from the user, must take the input as first argument and return the modified input
spliter_function: list[callable] = []
post_funcs: list[callable] = [] # Functions called at the end of the iteration


class Command():
    """
    A command for the console loop.
    -------------------------------------------------------------
    name : The string to write in the console to call the command.
    handler : The function to call when the command is used.
    arg_count : The number of argument that the handler function takes.
    """

    def __init__(self, name: str, handler: "function", arg_count: int) -> None:
        self.name = name
        self.handler = handler
        self.arg_count = arg_count

    def get_matching_score(self, command: str) -> int:
        """"Return the number of matching character in the command.
        If it's the exact command, return -1."""
        if command == self.name:
            return -1
        score = 0
        for i, letter in enumerate(command):
            if letter == self.name[i]:
                score += 1
            else:
                return score

        return score


_cmd_variables: dict[str:any] = {}

def set_variable_cmd(name: str, var_type: str, value: str) -> int:
    match var_type:
        case "str": pass
        case "int": value = int(value)
        case "float": value = float(value)
        case other: print(ERROR_PREFIX, 'at "set" : Unsupported type :', other)

    feedback = "variable "
    if _cmd_variables.get(name, None):
        if type(_cmd_variables[name]) == type(value):
            feedback += f"{name} changed from {_cmd_variables[name]} to "
        else:
            feedback += f"{name} changed from ({type(_cmd_variables[name]).__name__}) {_cmd_variables[name]} to ({var_type}) "
    else:
        feedback += f"{name} initialized to ({var_type}) "

    _cmd_variables[name] = value
    feedback += f"{value}"

    print(feedback)

SET_VARIABLE_COMMAND = Command("set", set_variable_cmd, 3)
commands.append(SET_VARIABLE_COMMAND)

def get_variable(name: str) -> str:
    if not name in _cmd_variables:
        print(ERROR_PREFIX, name, 'variable is not defined ! Returned "{name}"')
        return name

    print("$" + name, "→", str(_cmd_variables[name]))
    return str(_cmd_variables[name])

def handle_var(split_part: str) -> str:
    if split_part.startswith(VARIABLE_GETTER_PREFIX):
        return get_variable(split_part.removeprefix(VARIABLE_GETTER_PREFIX))
    else:
        return split_part


def pop_split(liste_of_split: list[str]) -> str:
    return handle_var(liste_of_split.pop(0))


def start_loop() -> None:
    """Start the main loop of the console."""

    global enabled
    enabled = True

    # Main Loop
    while enabled:
        # Calling all pre-iteration functions
        for function in pre_funcs: function()

        inputed = input(start_prompt)

        # Calling all input modifying functions
        for function in input_funcs: inputed = function(inputed)

        splited = inputed.split(" ")

        for i, v in enumerate(splited):
            for function in spliter_function: v = function(v)
            splited[i] = v


        while splited:
            current_cmd = pop_split(splited)
            found: None|function = None

            if splited and splited[0] == "=":
                found = SET_VARIABLE_COMMAND
                splited[0] = current_cmd
                current_cmd = "set"
            else:
                best_score = 0

                if current_cmd == stop_cmd:
                    enabled = False
                    break

                for command in commands:
                    current_score = command.get_matching_score(current_cmd)
                    if current_score == -1:
                        found = command
                        break
                    elif current_score > best_score:
                        found = command
                        best_score = current_score
                    elif current_score == best_score:
                        found = None

            if found:
                if len(splited) < found.arg_count:
                    print(ERROR_PREFIX, f"There was not enough argument given to `{command.name}` ({len(splited)} given but {found.arg_count} required)")

                try:
                    found.handler(*(pop_split(splited) for _ in range(found.arg_count)))
                except Exception as error:
                    print(ERROR_PREFIX, "A python error occured :")
                    print("═" * 30)
                    print_exc()
                    print("═" * 30)

            elif current_cmd in _cmd_variables:
                print(current_cmd, "=", _cmd_variables[current_cmd])
            else:
                print(command_error_prompt % current_cmd)

        if end_prompt:
            print(end_prompt)

        # Calling all post-iteration functions
        for function in post_funcs: function()


# Start automatically the loop if not loaded as a module
if __name__ == "__main__":
    start_loop()