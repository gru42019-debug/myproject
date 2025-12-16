import streamlit as st
st.title("Моето първо приложение")
name = st.text_input("Как се казваш")
if name:
  st.mute(f"Здравей,{name}!")
