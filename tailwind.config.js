/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "**/*.py",
      "**/*.html", 
      "**/*.js",     
    ],
    theme: {},
  
    plugins: [
      require("daisyui")
    ]
  }
  