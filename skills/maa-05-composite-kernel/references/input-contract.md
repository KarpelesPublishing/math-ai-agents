# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **step_success:** Marginal equal-step probability in [0,1] for separate constructed reliability cases.
- **steps:** Positive integer transition count up to 1000.
- **conditional_success:** List of probabilities conditioned on all previous steps succeeding, one per step; its length must equal steps.
- **chooser:** State by action row-stochastic matrix.
- **tool:** Action by next-state row-stochastic matrix.
- **initial:** Normalized state distribution matching the composed kernel.
- **assemblies:** Optional rows with name,budget,steps,observation,memory,retrieval,tool. Context maps are square stochastic matrices in the declared context encoding. Chooser stays fixed. Resource allowances must share units; actual consumed work is not measured.

## Valid transfer input

```json
{
  "step_success": 0.9,
  "steps": 3,
  "conditional_success": [
    0.9,
    0.8,
    0.7
  ],
  "chooser": [
    [
      1,
      0
    ],
    [
      0,
      1
    ]
  ],
  "tool": [
    [
      0.7,
      0.3
    ],
    [
      0.4,
      0.6
    ]
  ],
  "initial": [
    0.5,
    0.5
  ],
  "assemblies": [
    {
      "name": "complete",
      "budget": 100,
      "steps": 10,
      "observation": [
        [
          1,
          0
        ],
        [
          0,
          1
        ]
      ],
      "memory": [
        [
          1,
          0
        ],
        [
          0,
          1
        ]
      ],
      "retrieval": [
        [
          1,
          0
        ],
        [
          0,
          1
        ]
      ],
      "tool": [
        [
          0.7,
          0.3
        ],
        [
          0.4,
          0.6
        ]
      ]
    },
    {
      "name": "memory blurred",
      "budget": 120,
      "steps": 10,
      "observation": [
        [
          1,
          0
        ],
        [
          0,
          1
        ]
      ],
      "memory": [
        [
          0.5,
          0.5
        ],
        [
          0.5,
          0.5
        ]
      ],
      "retrieval": [
        [
          1,
          0
        ],
        [
          0,
          1
        ]
      ],
      "tool": [
        [
          0.7,
          0.3
        ],
        [
          0.4,
          0.6
        ]
      ]
    },
    {
      "name": "retrieval blurred",
      "budget": 100,
      "steps": 10,
      "observation": [
        [
          1,
          0
        ],
        [
          0,
          1
        ]
      ],
      "memory": [
        [
          1,
          0
        ],
        [
          0,
          1
        ]
      ],
      "retrieval": [
        [
          0.5,
          0.5
        ],
        [
          0.5,
          0.5
        ]
      ],
      "tool": [
        [
          0.7,
          0.3
        ],
        [
          0.4,
          0.6
        ]
      ]
    },
    {
      "name": "observation blurred",
      "budget": 100,
      "steps": 10,
      "observation": [
        [
          0.5,
          0.5
        ],
        [
          0.5,
          0.5
        ]
      ],
      "memory": [
        [
          1,
          0
        ],
        [
          0,
          1
        ]
      ],
      "retrieval": [
        [
          1,
          0
        ],
        [
          0,
          1
        ]
      ],
      "tool": [
        [
          0.7,
          0.3
        ],
        [
          0.4,
          0.6
        ]
      ]
    },
    {
      "name": "single transition",
      "budget": 100,
      "steps": 1,
      "observation": [
        [
          1,
          0
        ],
        [
          0,
          1
        ]
      ],
      "memory": [
        [
          1,
          0
        ],
        [
          0,
          1
        ]
      ],
      "retrieval": [
        [
          1,
          0
        ],
        [
          0,
          1
        ]
      ],
      "tool": [
        [
          0.7,
          0.3
        ],
        [
          0.4,
          0.6
        ]
      ]
    }
  ]
}
```
