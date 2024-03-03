# BeyondSilence（超越寂静）

> Keeping alive is much more important than keeping a will.
>
> You don't have to face things alone.

BeyondSilence recognizes prolonged user inactivity on GitHub (Max 89 days), offering a gentle acknowledgment by showing pre-set messages. It's designed to run on a public GitHub repository with GitHub Actions.

## Quick Start

### BEYONDSILENCE_CONFIG

```json
{
  "github_user_name": "MurataHimeko",
  "days_before": 15,
  "main_description": "这就是，最后一课了.....",
  "dump_config_when_triggered": true,
  "trigger_when_api_404": false,
  "messages": [
    {
      "environ": "MESSAGE1",
      "description": "姬子温柔地注视着你，不再言语。",
      "content": ""
    },
    {
      "environ": "MESSAGE2",
      "description": "琪亚娜，我已经没有什么能教你的了。",
      "content": ""
    }
  ]
}
```

### BEYONDSILENCE_KEYS

```json
{
  "MESSAGE1": "姬子温柔地注视着你",
  "MESSAGE2": "我已经没有什么能教你的了"
}
```

Run `gen_env.py` to get env variable `BEYONDSILENCE_CONFIG` and `BEYONDSILENCE_KEYS`.

Set `BEYONDSILENCE_CONFIG` and `BEYONDSILENCE_KEYS` in GitHub Actions Repository secrets.

Enable GitHub Actions.

The output when triggered will be written to `README.md`, for example:

```
GitHub user name: MurataHimeko

Last update time: 2024-01-07 19:04:42, triggered by inactivity of 15 days

Main description:
这就是，最后一课了.....

Messages:
MESSAGE1: 姬子温柔地注视着你，不再言语。
Value: 姬子温柔地注视着你

MESSAGE2: 琪亚娜，我已经没有什么能教你的了。
Value: 我已经没有什么能教你的了

End of output

```

Please be aware that BeyondSilence is not designed for large strings, there's a 48 KB limit in GitHub Action secrets.
