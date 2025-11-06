import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  docs: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/installation',
        'getting-started/quickstart',
        'getting-started/first-server',
      ],
    },
    {
      type: 'category',
      label: 'Core Concepts',
      collapsed: false,
      items: [
        'core-concepts/architecture',
        'core-concepts/tool-system',
        'core-concepts/dynamic-generation',
        'core-concepts/transport-detection',
      ],
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/loading-servers',
        'guides/using-tools',
        'guides/working-with-resources',
        'guides/authentication',
        'guides/type-generation',
        'guides/server-registry',
        'guides/error-handling',
        'guides/async-usage',
      ],
    },
    {
      type: 'category',
      label: 'Advanced Topics',
      items: [
        'advanced/tool-transformation',
        'advanced/argument-customization',
        'advanced/framework-integration',
        'advanced/custom-handlers',
        'advanced/sampling-elicitation',
      ],
    },
    {
      type: 'category',
      label: 'Examples',
      items: [
        'examples/basic-usage',
        'examples/ai-agents',
        'examples/workflow-automation',
        'examples/composition',
      ],
    },
    {
      type: 'category',
      label: 'Troubleshooting',
      items: [
        'troubleshooting/common-issues',
        'troubleshooting/faq',
      ],
    },
  ],

  api: [
    {
      type: 'category',
      label: 'API Reference',
      collapsed: false,
      items: [
        'api/loader',
        'api/tools',
        'api/resources',
        'api/prompts',
        'api/transformation',
        'api/codegen',
        'api/registry',
        'api/exceptions',
        'api/schema',
      ],
    },
  ],
};

export default sidebars;
