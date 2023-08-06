class UserInput():
    def take_user_input(self, userinputs):
        """
        The method take dict inputs for list of inputs to be taken,
        takes all input from user and returns back input taken
        :param inputs: Format for dict
        {
            "key": "Description to be show for input"
        }
        :return:
        {
            "key": "[INPUT_FROM_USER]"
        }
        """
        response = { }
        for key in userinputs:
            response[key] = input(userinputs[key] + "\n>> ")
        return response