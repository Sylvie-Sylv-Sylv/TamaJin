class JsonParser:
    def __init__(self, text):
        self.text = text
        self.i = 0

    def peek(self):
        if self.i >= len(self.text):
            return None
        return self.text[self.i]

    def consume(self):
        if self.i >= len(self.text):
            raise SyntaxError("Unexpected end")

        c = self.text[self.i]
        self.i += 1
        return c

    def expect(self, char):
        if self.consume() != char:
            raise SyntaxError(f"Expected {char}")

    def expect_str(self, string):
        for char in string:
            self.expect(char)

    def starts_with(self, word):
        return self.text[self.i : self.i + len(word)] == word

    def skip_whitespace(self):
        while self.i < len(self.text) and self.peek().isspace():
            self.i += 1

    # --------------------
    # values
    # --------------------

    def parse_value(self):
        self.skip_whitespace()

        c = self.peek()

        if c == '"':
            return self.parse_string()

        if c == "{":
            return self.parse_object()

        if c == "[":
            return self.parse_array()

        if c == "n":
            self.expect_str("null")
            return None

        if c == "t":
            self.expect_str("true")
            return True

        if c == "f":
            self.expect_str("false")
            return False

        if c == "-" or c.isdigit():
            return self.parse_number()

        raise SyntaxError("Invalid value")

    # --------------------
    # string
    # --------------------

    def parse_string(self):
        self.expect('"')

        result = ""

        while self.peek() != '"':
            result += self.consume()

        self.expect('"')

        return result

    # --------------------
    # number
    # --------------------

    def parse_number(self):
        start = self.i

        # sign
        if self.peek() == "-":
            self.consume()

        # integer part
        if self.peek() == "0":
            self.consume()
        elif self.peek() and self.peek().isdigit():
            if self.peek() == "0":
                raise SyntaxError()

            while self.peek() and self.peek().isdigit():
                self.consume()
        else:
            raise SyntaxError("Expected digit")

        # fraction
        if self.peek() == ".":
            self.consume()

            if not self.peek().isdigit():
                raise SyntaxError("Expected digit after .")

            while self.peek() and self.peek().isdigit():
                self.consume()

        # exponent
        if self.peek() in ("e", "E"):
            self.consume()

            if self.peek() in ("+", "-"):
                self.consume()

            if not self.peek().isdigit():
                raise SyntaxError("Expected exponent digit")

            while self.peek() and self.peek().isdigit():
                self.consume()

        value = self.text[start : self.i]

        if "." in value or "e" in value or "E" in value:
            return float(value)

        return int(value)

    # --------------------
    # array
    # --------------------

    def parse_array(self):
        arr = []

        self.expect("[")

        self.skip_whitespace()

        if self.peek() == "]":
            self.consume()
            return arr

        while True:
            arr.append(self.parse_value())

            self.skip_whitespace()

            c = self.consume()

            if c == "]":
                break

            if c != ",":
                raise SyntaxError("Expected , or ]")

        return arr

    # --------------------
    # object
    # --------------------

    def parse_object(self):
        obj = {}

        self.expect("{")

        self.skip_whitespace()

        if self.peek() == "}":
            self.consume()
            return obj

        while True:
            # key
            key = self.parse_string()

            self.skip_whitespace()

            self.expect(":")

            value = self.parse_value()

            obj[key] = value

            self.skip_whitespace()

            c = self.consume()

            if c == "}":
                break

            if c != ",":
                raise SyntaxError("Expected , or }")

            self.skip_whitespace()

        return obj
