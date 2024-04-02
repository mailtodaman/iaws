Terraformer
=======

Introduction
------------

ChatGPT is a powerful AI model developed by OpenAI for generating human-like text. This section will guide you through integrating ChatGPT into your project.

Setup
-----

To set up ChatGPT:

1. Ensure you have an API key from OpenAI.
2. Install the necessary libraries.
3. Configure your application to use ChatGPT.

Code Example
------------

.. code-block:: python

   import openai

   openai.api_key = 'your-api-key-here'

   response = openai.Completion.create(
     engine="text-davinci-003",
     prompt="Hello, world!",
     temperature=0.5,
     max_tokens=64,
     top_p=1.0,
     frequency_penalty=0.0,
     presence_penalty=0.0
   )

   print(response.choices[0].text.strip())
