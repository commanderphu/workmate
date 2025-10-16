// eslint.config.js
import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import vue from 'eslint-plugin-vue'
import prettier from 'eslint-plugin-prettier'

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...vue.configs['flat/recommended'], // <-- wichtig: Flat-Config für ESLint 9
  {
    files: ['**/*.{ts,js,vue}'],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'module'
    },
    plugins: {
      prettier
    },
    rules: {
      'vue/multi-word-component-names': 'off',
      '@typescript-eslint/no-unused-vars': 'warn',
      'no-console': 'warn',
      'prettier/prettier': ['warn', { singleQuote: true, semi: false }]
    }
  }
]
