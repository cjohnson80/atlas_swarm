# Project Scratchpad

Goal: Build a hello world project in workspace/hello_world

## Acceptance Criteria
API Error 429: {
  "error": {
    "code": 429,
    "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_requests_per_model_per_day, limit: 250, model: gemini-3-pro\nPlease retry in 9m45.678451187s.",
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.Help",
        "links": [
          {
            "description": "Learn more about Atlas API quotas",
            "url": "https://ai.google.dev/gemini-api/docs/rate-limits"
          }
        ]
      },
      {
        "@type": "type.googleapis.com/google.rpc.QuotaFailure",
        "violations": [
          {
            "quotaMetric": "generativelanguage.googleapis.com/generate_requests_per_model_per_day",
            "quotaId": "GenerateRequestsPerDayPerProjectPerModel",
            "quotaDimensions": {
              "location": "global",
              "model": "gemini-3-pro"
            },
            "quotaValue": "250"
          }
        ]
      },
      {
        "@type": "type.googleapis.com/google.rpc.RetryInfo",
        "retryDelay": "585s"
      }
    ]
  }
}


## Architecture
(To be defined by Architect)
