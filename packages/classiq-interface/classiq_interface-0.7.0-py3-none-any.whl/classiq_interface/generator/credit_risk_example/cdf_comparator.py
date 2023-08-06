from classiq_interface.generator.arith import binary_ops
from classiq_interface.generator.arith.register_user_input import RegisterUserInput


class CDFComparator(binary_ops.LessEqual):
    def _create_io_names(self):
        if isinstance(self.left_arg, RegisterUserInput) and isinstance(
            self.right_arg, RegisterUserInput
        ):
            if (
                self.left_arg.name is None
                or self.right_arg.name is None
                or self.output_name is None
            ):
                raise ValueError(
                    f"CDF comparator requires valid argument names. Got: {self.left_arg.name}, {self.right_arg.name}, {self.output_name}"
                )
            self._input_names = [self.left_arg.name, self.right_arg.name]
            self._output_names = [
                self.output_name,
                self.left_arg.name,
                self.right_arg.name,
            ]
            return

        if isinstance(self.left_arg, RegisterUserInput):
            arg_name = self.left_arg.name
        else:
            assert isinstance(
                self.right_arg, RegisterUserInput
            ), "At least one argument should be a register"
            arg_name = self.right_arg.name

        if arg_name is None or self.output_name is None:
            raise ValueError(
                f"CDF comparator requires valid argument names. Got: {arg_name}, {self.output_name}"
            )
        self._input_names = [arg_name]
        self._output_names = [self.output_name, arg_name]
