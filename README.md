# ChatAI
**ChatAI** is a Telegram Bot that can generate Text Completion. The Bot uses powerful engines of **OpenAI** and generates Text Completion right in Telegram.

**ChatAI** is **OpenAI** but for **Telegram.**

**Check Out [**ChatAI**](https://web.telegram.org/k/#@chat_with_ai_bot)**

## Features

- `Text Completion`
- `Inline Queries`
- `Generate Probabilities`

  ### Text Completion
  The **Text Completion** feature uses powerful engines of OpenAI and generates Text Completion right in Telegram.

  ![Text Completion](https://user-images.githubusercontent.com/110465395/207259744-a4ac02ac-734f-495f-a3b8-292f09a1a507.png)

  *The Text completion will be generated with the user's settings.*

  ### Inline Query
  The **Inline Query** feature enables users to generate Text Completion right from **any chat** (Chat with your friends and family).
  You can simply write `@chat_with_ai_bot` in any chat and enjoy Text Completion.

  ![Inline Query](https://user-images.githubusercontent.com/110465395/207078992-a788b5e5-dd78-4273-840f-576944df77ac.png)

  *The Text completion will be generated with the user's settings.*

  ### Generate Probabilities
  **Generate Probabilities** is a feature for users (geeks) to analyze the Likelihood of a `Token` being generated. \
  You can enable the feature by `/gen_probs` command.

  ``` Telegram
  /gen_probs      # For GUI
  # or 
  /gen_probs 1    # Direct Enablement
  ```

  ![Generate Probabilities](https://user-images.githubusercontent.com/110465395/207262727-8039ad08-ac41-490c-b317-40407c819fb0.png)
  ![Generated Probabilities](https://user-images.githubusercontent.com/110465395/207263888-9ce9e5d2-fd13-4c54-bee8-7f298c7c56d8.png)
  *The Text completion will be generated with the user's settings.*
  

## Commands
You can use the `commands` to change the settings for your Text Completion process.

#### Bot Commands
| Commands | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `/start` | `Command` | Start Bot |
| `/chat` | `Command` | Start chatting with OpenAI |
| `/help` | `Command` | Get Help |
| `/exit` | `Command` | Exit OpenAI Prompt |
| `/commands` | `Command` | Get all OpenAI commands |
| `/default` | `Command` | Fall back to default settings |
| `/contact` | `Command` | Connect with me |

#### OpenAI Commands
| Commands | Type     | Description                | Values                       |
| :-------- | :------- | :------------------------- | :------------------------- |
| `/model ` | `Command` | The model which will generate the completion. | `text-davinci-003` <br /> `text-curie-001`
| `/temperature ` | `Command` | Control Randomness. |
| `/max_length ` | `Command` | Maximum number of tokens to generate. |
| `/stop ` | `Command` | n sequences where the API will stop generating further tokens. |
| `/top_p ` | `Command` | Top probability Tokens. |
| `/frequency_penalty` | `Command` | Decreasing the model's likelihood to repeat the same line verbatim. |
| `/presence_penalty ` | `Command` | Increasing the model's likelihood to talk about new topics. |
| `/best_of ` | `Command` | Generate multiple completion on the server:side and return only the best. |
| `/n` | `Command` | How many completions to generate for each prompt. |
| `/gen_probs ` | `Command` | Generate a full spectrum probabilities of tokens. |
| `/echo` | `Command` | Echo back the prompt in addition to the completion. |

## Check Out [**ChatAI**](https://web.telegram.org/k/#@chat_with_ai_bot)

## Authors

- [@lunatic_sain](https://twitter.com/lunatic_sain)


## 🚀 About Me
I'm a Data Science geek and Developer.

[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/hussainkhatumdi)
[![twitter](https://img.shields.io/badge/twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/lunatic_sain)

## Acknowledgements

 - [OpenAI Playground](https://beta.openai.com/playground?model=text-davinci-003)
 

## Tech Stack

**Language:** `python`

**API:** `Telegram-bot-api` `Openai`

**Server:** `Heroku`


## Support

For support, email hussainkhatumdi67+chatai@gmail.com

![ChatAI Banner](https://user-images.githubusercontent.com/110465395/207267370-ebd8f678-f292-4ddd-85f3-812a0e399649.png)
