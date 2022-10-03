mkdir -p ~/.streamlit/

# add the config details to the ‘config.toml’ file
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml