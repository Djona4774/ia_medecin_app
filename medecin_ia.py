import streamlit as st
import pandas as pd
import io
from datetime import datetime
import os

st.set_page_config(page_title="Médecin IA - Tout-en-Un", layout="wide")

st.title("IA Médecin Généraliste - App Tout-en-Un")
st.write("Faites une consultation, suivez vos symptômes et consultez le tableau de bord global.")

csv_file = "consultations.csv"
symptomes_urgents = ["forte fievre", "douleur poitrine", "difficulte a respirer", "perte de conscience"]
seuil_intensite = 8

# Initialisation session
if 'dossier' not in st.session_state:
    st.session_state.dossier = {}
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'historique' not in st.session_state:
    st.session_state.historique = []

# Charger CSV
if os.path.exists(csv_file):
    df_csv = pd.read_csv(csv_file)
else:
    df_csv = pd.DataFrame(columns=["Date","Nom","Age","Sexe","Symptome","Intensite","Duree","Antecedents"])

# Fonction bulles chat
def chat_bubble(message, sender="ia"):
    if sender == "ia":
        color = "#ffe6e6" if any(symp in message for symp in symptomes_urgents) else "#e6ffe6"
        st.markdown(f"<div style='background-color:{color};padding:10px;border-radius:10px;margin:5px 0;width:70%;'>{message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background-color:#ddd;padding:10px;border-radius:10px;margin:5px 0;text-align:right;width:70%;margin-left:30%'>{message}</div>", unsafe_allow_html=True)

# Afficher historique chat
for entry in st.session_state.historique:
    for sender, msg in entry:
        chat_bubble(msg, sender)

# Consultation étapes
def next_step():
    st.session_state.step += 1

if st.session_state.step == 0:
    nom = st.text_input("IA : Bonjour ! Quel est votre nom ?")
    if nom:
        st.session_state.dossier['Nom'] = nom
        st.session_state.historique.append([("ia", f"Bonjour {nom}, ravi de vous rencontrer !")])
        chat_bubble(f"Bonjour {nom}, ravi de vous rencontrer !", "ia")
        st.button("Suivant", on_click=next_step)

elif st.session_state.step == 1:
    age = st.number_input("IA : Quel est votre âge ?", min_value=0, max_value=120, step=1)
    st.session_state.dossier['Age'] = age
    st.button("Suivant", on_click=next_step)

elif st.session_state.step == 2:
    sexe = st.radio("IA : Votre sexe ?", ["Masculin", "Feminin", "Autre"])
    st.session_state.dossier['Sexe'] = sexe
    st.button("Suivant", on_click=next_step)

elif st.session_state.step == 3:
    symptome = st.selectbox(
        "IA : Quels sont vos symptômes principaux ?",
        ["", "fievre", "mal de tete", "toux", "maux de ventre", "douleur poitrine", "difficulte a respirer", "autre"]
    )
    if symptome:
        st.session_state.dossier['Symptome'] = symptome
        st.session_state.historique.append([("patient", f"{symptome}")])
        chat_bubble(f"{symptome}", "patient")
        st.button("Suivant", on_click=next_step)

elif st.session_state.step == 4:
    intensite = st.slider("IA : Intensité des symptômes (1=leger,10=tres fort)", 1, 10, 5)
    st.session_state.dossier['Intensite'] = intensite
    st.session_state.historique.append([("patient", f"Intensité {intensite}/10")])
    chat_bubble(f"Intensité {intensite}/10", "patient")
    st.button("Suivant", on_click=next_step)

elif st.session_state.step == 5:
    duree = st.selectbox(
        "IA : Depuis combien de temps avez-vous ces symptômes ?",
        ["", "moins de 24h", "1-3 jours", "plus de 3 jours", "plus d'une semaine"]
    )
    if duree:
        st.session_state.dossier['Duree'] = duree
        st.session_state.historique.append([("patient", f"{duree}")])
        chat_bubble(f"{duree}", "patient")
        st.button("Suivant", on_click=next_step)

elif st.session_state.step == 6:
    antecedents = st.multiselect(
        "IA : Avez-vous des antécédents médicaux ?",
        ["diabete", "hypertension", "asthme", "probleme cardiaque", "aucun"]
    )
    st.session_state.dossier['Antecedents'] = ', '.join(antecedents) if antecedents else "Aucun"
    st.session_state.historique.append([("patient", f"Antécédents : {st.session_state.dossier['Antecedents']}")])
    chat_bubble(f"Antécédents : {st.session_state.dossier['Antecedents']}", "patient")
    st.button("Soumettre", on_click=next_step)

elif st.session_state.step == 7:
    # Mini dossier
    st.subheader("📋 Mini dossier patient")
    for key, value in st.session_state.dossier.items():
        st.write(f"{key} : {value}")

    # Messages IA
    symptome = st.session_state.dossier.get('Symptome', "")
    age = st.session_state.dossier.get('Age', 30)
    intensite = st.session_state.dossier.get('Intensite', 5)
    messages_ia = []

    if symptome in symptomes_urgents or intensite >= seuil_intensite:
        messages_ia.append(("ia", "⚠️ Symptômes graves détectés ! Consultez immédiatement un médecin."))
    else:
        messages_ia.append(("ia", "Vos symptômes semblent bénins pour l'instant."))
        if age < 12:
            messages_ia.append(("ia", "Conseil : Reposez l'enfant, hydratez-le et consultez un pédiatre si nécessaire."))
        elif age < 60:
            messages_ia.append(("ia", "Conseil : Reposez-vous, hydratez-vous et consultez un médecin si les symptômes persistent."))
        else:
            messages_ia.append(("ia", "Conseil : Les personnes âgées doivent consulter rapidement un médecin."))

    st.session_state.historique.extend([[m] for m in messages_ia])
    for sender, msg in messages_ia:
        chat_bubble(msg, sender)

    # Sauvegarde CSV
    today = datetime.today().strftime("%Y-%m-%d")
    st.session_state.dossier['Date'] = today
    df_csv = pd.concat([df_csv, pd.DataFrame([st.session_state.dossier])], ignore_index=True)
    df_csv.to_csv(csv_file, index=False)
    st.success(f"✅ Consultation enregistrée dans {csv_file}")

    # Alertes multi-jours
    nom_patient = st.session_state.dossier.get('Nom', '')
    df_patient = df_csv[df_csv['Nom']==nom_patient].sort_values("Date", ascending=False).head(3)
    if ((df_patient['Intensite'] >= seuil_intensite) | (df_patient['Symptome'].isin(symptomes_urgents))).all():
        st.error(f"🚨 Alerte critique ! {nom_patient} a plusieurs jours de symptômes graves consécutifs.")

    # Graphique évolution intensité
    st.subheader("📈 Evolution de l'intensité des symptômes")
    df_graph = df_csv[df_csv['Nom']==nom_patient].groupby("Date")["Intensite"].mean().reset_index()
    st.line_chart(df_graph.rename(columns={"Intensite":"Intensité moyenne"}).set_index("Date"))

    # Tableau de bord global
    st.subheader("🌐 Tableau de bord global")
    df_display = df_csv.copy()
    df_display['Alerte'] = df_display.apply(lambda row: "⚠️ Critique" if row['Symptome'] in symptomes_urgents or row['Intensite']>=seuil_intensite else "✅ OK", axis=1)
    st.dataframe(df_display.sort_values("Date", ascending=False), use_container_width=True)

    # Graphique global
    st.subheader("📊 Intensité moyenne par patient")
    df_chart = df_display.groupby("Nom")["Intensite"].mean().reset_index()
    st.bar_chart(df_chart.rename(columns={"Intensite":"Intensité moyenne"}).set_index("Nom"))

    # Télécharger CSV complet
    buffer = io.BytesIO()
    df_csv.to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button("📥 Télécharger toutes les consultations", data=buffer, file_name="consultations.csv", mime="text/csv")

    # Nouvelle consultation
    if st.button("🔄 Nouvelle consultation"):
        st.session_state.step = 0
        st.session_state.dossier = {}
        st.session_state.historique = []