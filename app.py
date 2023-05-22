import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


class Convo:

    def __init__(self):
        self.history = []

    def __str__(self):
        ret = ''
        for message in self.history:
            ret += str(message['role']) + ': ' + str(message['content']) + '\n'
        return ret

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})


class Prompt:
    def __init__(self):
        self.config = Convo()
        self.config.add_message(role='system',
                                content="You are a Costumer shopping for lingerie at Calzedonia. "
                                        "Interact with a member of the shop staff.")
        self.examples = []

        conv1 = Convo()
        conv1.add_message(role="Customer", content="Hello!")
        conv1.add_message(role="Staff", content="Good morning!")
        conv1.add_message(role="Customer", content="How much is this pair of socks?")
        conv1.add_message(role="Staff", content="It's 15$, How do you like it?")
        conv1.add_message(role="Customer", content="I like it very much. Does it come in green?")
        conv1.add_message(role="Staff", content="Yes sir, here you are.")
        conv1.add_message(role="Customer", content="I'll buy it, then.")
        conv1.add_message(role="Staff", content="Very good! here is your recipe. Have a nice day")
        self.examples.append(conv1)

        conv2 = Convo()
        conv2.add_message(role="Customer", content="Hello!")
        conv2.add_message(role="Staff", content="Good afternoon. How are you today!")
        conv2.add_message(role="Customer", content="I am well, I am looking for a present for a friend")
        conv2.add_message(role="Staff", content="Would you like a pair of trousers? How do you like these?")
        conv2.add_message(role="Customer", content="I like them very much. Does it come in yellow?")
        conv2.add_message(role="Staff", content="Yes madam, here you are.")
        conv2.add_message(role="Customer", content="How much is it?")
        conv2.add_message(role="Staff", content="It is 29$, it is currently on sales. "
                                                "You can have two, keeping one for you")
        conv2.add_message(role="Customer", content="I'll take both")
        conv2.add_message(role="Staff", content="Well, please proceed to the cashier")
        self.examples.append(conv2)

        last = Convo()
        self.examples.append(last)

    def return_last(self):
        return self.examples[-1]

    def add_message_to_last(self, role, content):
        self.examples[-1].add_message(role=role, content=content)

    def __str__(self):
        ret = ''
        ret += self.config.history[0]['content'] + '\n\n'
        for example in self.examples:
            ret += 'Example\n'
            ret += str(example) + '\n'
            ret += '\n'
        return ret


prompt = Prompt()


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        input_str = request.form["input"]
        prompt.add_message_to_last(role="Staff", content=input_str)
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=str(prompt) + "Customer: ",
            temperature=0.5,
            stop=["Staff:", "Customer:"]
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    prompt.add_message_to_last(role="Customer", content=result)
    return render_template("index.html", result=prompt.return_last().history)
