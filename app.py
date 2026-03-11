"""
Application Web - Calculateur de Cycle Frigorifique
Développée par Christian Lucas
Version web reproduisant l'interface desktop
"""
import streamlit as st
import streamlit.components.v1 as components
from CoolProp.CoolProp import PropsSI
import CoolProp
import numpy as np
from PIL import Image
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── AdSense ──────────────────────────────────────────────────────────────────
# Remplacez VOTRE_PUB_ID et VOTRE_SLOT_ID par vos identifiants AdSense réels
ADSENSE_PUB_ID  = "ca-pub-3837526753617519"
ADSENSE_SLOT_ID = "8113621558"

def afficher_pub_adsense(format_pub="horizontal"):
    """Affiche une unité publicitaire AdSense via st.components.v1.html()."""
    if format_pub == "horizontal":
        w, h = 728, 90
    elif format_pub == "carre":
        w, h = 300, 250
    else:  # rectangle
        w, h = 336, 280

    html_ad = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script async
            src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUB_ID}"
            crossorigin="anonymous">
        </script>
    </head>
    <body style="margin:0;padding:0;background:transparent;">
        <ins class="adsbygoogle"
             style="display:inline-block;width:{w}px;height:{h}px"
             data-ad-client="{ADSENSE_PUB_ID}"
             data-ad-slot="{ADSENSE_SLOT_ID}">
        </ins>
        <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </body>
    </html>
    """
    components.html(html_ad, width=w + 10, height=h + 10, scrolling=False)


# Configuration de la page
st.set_page_config(
    page_title="Calculateur de Cycle Frigorifique",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé pour reproduire le style desktop
st.markdown("""
    <style>
    /* Couleurs de la charte graphique */
    :root {
        --color-bg-main: #f8fafc;
        --color-card: #ffffff;
        --color-text-primary: #0f172a;
        --color-text-secondary: #64748b;
        --color-border: #e2e8f0;
        --color-button: #2563eb;
        --color-button-validate: #10b981;
    }
    
    .main-container {
        background-color: var(--color-bg-main);
        padding: 10px;
    }
    
    .card {
        background-color: var(--color-card);
        border: 3px solid black;
        border-radius: 12px;
        padding: 15px;
        margin: 5px;
    }
    
    .card-title {
        font-size: 12px;
        font-weight: bold;
        color: var(--color-text-primary);
        margin-bottom: 10px;
    }
    
    .result-box {
        border-radius: 6px;
        border: 2px solid;
        padding: 8px;
        margin: 2px 0;
        height: 60px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .result-box-green {
        background-color: #ecfdf5;
        border-color: #10b981;
    }
    
    .result-box-red {
        background-color: #fef2f2;
        border-color: #ef4444;
    }
    
    .result-box-blue {
        background-color: #eff6ff;
        border-color: #3b82f6;
    }
    
    .result-label {
        font-size: 9px;
        font-weight: bold;
        color: var(--color-text-secondary);
    }
    
    .result-value {
        font-size: 10px;
        font-weight: bold;
    }
    
    .value-green {
        color: #059669;
    }
    
    .value-red {
        color: #dc2626;
    }
    
    .value-blue {
        color: #1e40af;
    }
    
    .schema-label {
        font-size: 9px;
        font-weight: bold;
        margin: 1px 0;
    }
    
    .label-blue {
        color: #2563eb;
    }
    
    .label-red {
        color: #dc2626;
    }
    
    .table-header {
        font-family: 'Segoe UI', sans-serif;
        font-size: 10px;
        font-weight: bold;
    }
    
    .table-cell {
        font-family: 'Segoe UI', sans-serif;
        font-size: 10px;
        font-weight: bold;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        padding: 10px 20px;
        background-color: white;
        border-radius: 8px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2563eb;
        color: white;
    }
    
    /* Masquer les éléments Streamlit par défaut */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Liste des fluides frigorigènes
FLUIDES = [
    "R134a", "R410A", "R32", "R404A", "R407C", "R290",
    "R744 (CO2)", "R717 (Ammoniac)", "R1234yf", "R1234ze",
    "R600a", "R449A", "R452A", "R454B", "R513A", "R407F",
    "R22", "R123", "R1270", "R152a", "R507A", "R422D",
    "R12", "R11"
]

# Mappage des noms d'affichage vers les noms CoolProp
FLUIDES_COOLPROP = {
    "R134a": "R134a",
    "R410A": "R410A",
    "R32": "R32",
    "R404A": "R404A",
    "R407C": "R407C",
    "R290": "R290",
    "R744 (CO2)": "CO2",
    "R717 (Ammoniac)": "NH3",
    "R1234yf": "R1234yf",
    "R1234ze": "R1234ze(E)",
    "R600a": "R600a",
    "R449A": "R449A.mix",
    "R452A": "R452A.mix",
    "R454B": "R454B.mix",
    "R513A": "R513A.mix",
    "R407F": "R407F",
    "R22": "R22",
    "R123": "R123",
    "R1270": "R1270",
    "R152a": "R152a",
    "R507A": "R507A",
    "R422D": "R422D",
    "R12": "R12",
    "R11": "R11"
}

def resource_path(relative_path):
    """Obtenir le chemin absolu d'une ressource"""
    return os.path.join(os.path.dirname(__file__), relative_path)

def obtenir_fluide_coolprop(fluide_affichage):
    """Convertit le nom d'affichage en nom CoolProp"""
    if fluide_affichage in FLUIDES_COOLPROP:
        return FLUIDES_COOLPROP[fluide_affichage]
    
    # Gestion spéciale pour R1234ze
    if fluide_affichage == "R1234ze":
        for variant in ["R1234ze(E)", "R1234ze(Z)", "R1234ze"]:
            try:
                PropsSI('T', 'P', 101325, 'Q', 0, variant)
                return variant
            except:
                continue
    
    return fluide_affichage

def calculer_propriete(fluide, prop, **kwargs):
    """Calcule une propriété thermodynamique avec gestion d'erreurs.

    PropsSI utilise la syntaxe: PropsSI(output, name1, value1, name2, value2, fluid)
    Cette fonction convertit les kwargs en arguments positionnels.
    """
    try:
        # Convertir kwargs en liste d'arguments positionnels pour PropsSI
        args = []
        for key, value in kwargs.items():
            args.extend([key, value])
        return PropsSI(prop, *args, fluide)
    except Exception as e:
        return None

def mettre_a_jour_pression_evaporation():
    """Met à jour la pression d'évaporation à partir de la température"""
    try:
        fluide_affichage = st.session_state.fluide
        fluide = obtenir_fluide_coolprop(fluide_affichage)
        
        to = st.session_state.get('to_evaporation')
        if to is not None:
            temp_evap_k = to + 273.15
            try:
                pression_evap_pa = calculer_propriete(fluide, 'P', T=temp_evap_k, Q=1)
            except:
                try:
                    pression_evap_pa = calculer_propriete(fluide, 'P', T=temp_evap_k, Q=0.5)
                except:
                    pression_evap_pa = calculer_propriete(fluide, 'P', T=temp_evap_k, Q=0)
            
            if pression_evap_pa:
                pression_evap_bar = pression_evap_pa / 1e5
                old_po = st.session_state.get('po_evaporation')
                if old_po is None or abs(old_po - pression_evap_bar) > 0.001:  # Seulement si changement significatif
                    st.session_state.po_evaporation = pression_evap_bar
    except:
        pass

def mettre_a_jour_pression_condensation():
    """Met à jour la pression de condensation à partir de la température"""
    try:
        fluide_affichage = st.session_state.fluide
        fluide = obtenir_fluide_coolprop(fluide_affichage)
        
        tc = st.session_state.get('tc_condensation')
        if tc is not None:
            temp_cond_k = tc + 273.15
            try:
                pression_cond_pa = calculer_propriete(fluide, 'P', T=temp_cond_k, Q=0)
            except:
                try:
                    pression_cond_pa = calculer_propriete(fluide, 'P', T=temp_cond_k, Q=0.5)
                except:
                    pression_cond_pa = calculer_propriete(fluide, 'P', T=temp_cond_k, Q=1)
            
            if pression_cond_pa:
                pression_cond_bar = pression_cond_pa / 1e5
                old_pk = st.session_state.get('pk_condensation')
                if old_pk is None or abs(old_pk - pression_cond_bar) > 0.001:  # Seulement si changement significatif
                    st.session_state.pk_condensation = pression_cond_bar
    except:
        pass

def mettre_a_jour_temperature_evaporation():
    """Met à jour la température d'évaporation à partir de la pression"""
    try:
        fluide_affichage = st.session_state.fluide
        fluide = obtenir_fluide_coolprop(fluide_affichage)
        
        po = st.session_state.get('po_evaporation')
        if po is not None:
            pression_evap_pa = po * 1e5
            try:
                temp_evap_k = calculer_propriete(fluide, 'T', P=pression_evap_pa, Q=1)
            except:
                try:
                    temp_evap_k = calculer_propriete(fluide, 'T', P=pression_evap_pa, Q=0.5)
                except:
                    temp_evap_k = calculer_propriete(fluide, 'T', P=pression_evap_pa, Q=0)
            
            if temp_evap_k:
                temp_evap = temp_evap_k - 273.15
                old_to = st.session_state.get('to_evaporation')
                if old_to is None or abs(old_to - temp_evap) > 0.01:  # Seulement si changement significatif
                    st.session_state.to_evaporation = temp_evap
    except:
        pass

def mettre_a_jour_temperature_condensation():
    """Met à jour la température de condensation à partir de la pression"""
    try:
        fluide_affichage = st.session_state.fluide
        fluide = obtenir_fluide_coolprop(fluide_affichage)
        
        pk = st.session_state.get('pk_condensation')
        if pk is not None:
            pression_cond_pa = pk * 1e5
            try:
                temp_cond_k = calculer_propriete(fluide, 'T', P=pression_cond_pa, Q=0)
            except:
                try:
                    temp_cond_k = calculer_propriete(fluide, 'T', P=pression_cond_pa, Q=0.5)
                except:
                    temp_cond_k = calculer_propriete(fluide, 'T', P=pression_cond_pa, Q=1)
            
            if temp_cond_k:
                temp_cond = temp_cond_k - 273.15
                old_tc = st.session_state.get('tc_condensation')
                if old_tc is None or abs(old_tc - temp_cond) > 0.01:  # Seulement si changement significatif
                    st.session_state.tc_condensation = temp_cond
    except:
        pass

def calculer_cycle():
    """Calcule le cycle frigorifique complet"""
    fluide_affichage = st.session_state.fluide
    fluide = obtenir_fluide_coolprop(fluide_affichage)

    to = st.session_state.get('to_evaporation')
    po = st.session_state.get('po_evaporation')
    surchauffe_utile = st.session_state.get('surchauffe_utile', 5.0) or 5.0
    echauffement_sup = st.session_state.get('echauffement_sup', 0.0) or 0.0

    tc = st.session_state.get('tc_condensation')
    pk = st.session_state.get('pk_condensation')
    sous_refroid_cond = st.session_state.get('sous_refroid_cond', 5.0) or 5.0
    refroidissement_sup = st.session_state.get('refroidissement_sup', 0.0) or 0.0

    rendement_vol = st.session_state.get('rendement_vol', 0.85) or 0.85
    rendement_isen = st.session_state.get('rendement_isen', 0.76) or 0.76

    type_metrique = st.session_state.get('type_metrique', 'Puissance frigorifique utile')
    valeur_metrique = st.session_state.get('valeur_metrique', 0.0)

    if not valeur_metrique or valeur_metrique <= 0:
        st.error("Veuillez entrer une valeur valide pour la métrique sélectionnée (Volume balayé ou Puissance frigorifique)")
        return None

    try:
        # Point 0 : Évaporation
        if po is not None and po > 0:
            p0 = po * 1e5
            t0_sat_result = calculer_propriete(fluide, 'T', P=p0, Q=0)
            if t0_sat_result is None:
                st.error(f"Impossible de calculer la température de saturation pour P={po} bar")
                return None
            t0_sat = t0_sat_result - 273.15
            if to is None or to == 0:
                to = t0_sat
        elif to is not None and to != 0:
            t0_k = to + 273.15
            p0 = calculer_propriete(fluide, 'P', T=t0_k, Q=0)
            if p0 is None:
                st.error(f"Impossible de calculer la pression de saturation pour T={to} °C")
                return None
        else:
            st.error("Veuillez entrer soit la température soit la pression d'évaporation")
            return None

        # Point 1 : Sortie évaporateur
        if to is None or to == 0:
            st.error("La température d'évaporation est requise")
            return None
        t1 = to + surchauffe_utile + echauffement_sup
        t1_k = t1 + 273.15
        p1 = p0
        h1 = calculer_propriete(fluide, 'H', T=t1_k, P=p1)
        s1 = calculer_propriete(fluide, 'S', T=t1_k, P=p1)
        v1 = calculer_propriete(fluide, 'D', T=t1_k, P=p1)

        if h1 is None or s1 is None:
            st.error("Erreur lors du calcul des propriétés au point 1 (sortie évaporateur)")
            return None

        if v1 and v1 > 0:
            v1 = 1.0 / v1
        else:
            st.error("Erreur lors du calcul du volume massique au point 1")
            return None

        # Point 2is : Compression isentropique
        if pk is not None and pk > 0:
            p2 = pk * 1e5
        elif tc is not None and tc != 0:
            tc_k = tc + 273.15
            p2 = calculer_propriete(fluide, 'P', T=tc_k, Q=0)
            if p2 is None:
                st.error(f"Impossible de calculer la pression de condensation pour T={tc} °C")
                return None
        else:
            st.error("Veuillez entrer soit la température soit la pression de condensation")
            return None

        s2is = s1  # Entropie en J/(kg·K)
        h2is = calculer_propriete(fluide, 'H', S=s2is, P=p2)
        t2is_result = calculer_propriete(fluide, 'T', S=s2is, P=p2)

        # Si le calcul direct échoue (mélanges comme R513A), utiliser méthode itérative
        if h2is is None or t2is_result is None:
            try:
                # Méthode itérative par bisection (comme dans main.py)
                temp_cond_sat = PropsSI('T', 'P', p2, 'Q', 0, fluide)
                temp_low = temp_cond_sat + 10
                temp_high = temp_cond_sat + 150

                for _ in range(30):
                    temp_est = (temp_low + temp_high) / 2
                    s_est = PropsSI('S', 'P', p2, 'T', temp_est, fluide)  # J/(kg·K)
                    if abs(s_est - s1) < 0.5:  # Tolérance en J/(kg·K)
                        h2is = PropsSI('H', 'P', p2, 'T', temp_est, fluide)  # J/kg
                        t2is_result = temp_est
                        break
                    if s_est < s1:
                        temp_low = temp_est
                    else:
                        temp_high = temp_est
                else:
                    temp_est = (temp_low + temp_high) / 2
                    h2is = PropsSI('H', 'P', p2, 'T', temp_est, fluide)  # J/kg
                    t2is_result = temp_est
            except Exception as e:
                st.error(f"Erreur lors du calcul de la compression isentropique (point 2is): {str(e)}")
                return None

        if h2is is None or t2is_result is None:
            st.error("Erreur lors du calcul de la compression isentropique (point 2is)")
            return None

        t2is = t2is_result - 273.15

        # Point 2 : Compression réelle
        h2 = h1 + (h2is - h1) / rendement_isen  # Tout en J/kg
        t2_result = calculer_propriete(fluide, 'T', H=h2, P=p2)
        s2 = calculer_propriete(fluide, 'S', H=h2, P=p2)

        # Fallback pour t2 si calcul direct échoue
        if t2_result is None:
            try:
                temp_cond_sat = PropsSI('T', 'P', p2, 'Q', 0, fluide)
                t2_result = temp_cond_sat + 30
            except:
                pass

        if t2_result is None:
            st.error("Erreur lors du calcul de la température de refoulement (point 2)")
            return None
        t2 = t2_result - 273.15

        # Point 3 : Condensation
        tc_sat_result = calculer_propriete(fluide, 'T', P=p2, Q=0)
        if tc_sat_result is None:
            st.error("Erreur lors du calcul de la température de saturation à la condensation")
            return None
        tc_sat = tc_sat_result - 273.15
        if tc is None or tc == 0:
            tc = tc_sat
        h3 = calculer_propriete(fluide, 'H', P=p2, Q=0)
        t3 = tc

        if h3 is None:
            st.error("Erreur lors du calcul de l'enthalpie au point 3")
            return None

        # Point 3' : Sortie condenseur
        t3p = tc - sous_refroid_cond - refroidissement_sup
        t3p_k = t3p + 273.15
        p3p = p2
        h3p = calculer_propriete(fluide, 'H', T=t3p_k, P=p3p)

        if h3p is None:
            st.error("Erreur lors du calcul de l'enthalpie au point 3' (sortie condenseur)")
            return None

        # Point 4 : Détente (isenthalpique)
        h4 = h3p
        p4 = p0

        # Calcul du titre x4 avec fallback pour mélanges
        x4 = calculer_propriete(fluide, 'Q', H=h4, P=p4)
        if x4 is None:
            try:
                # Méthode alternative : calcul manuel du titre
                h4_liquide = PropsSI('H', 'P', p4, 'Q', 0, fluide)
                h4_vapeur = PropsSI('H', 'P', p4, 'Q', 1, fluide)
                if h4_vapeur != h4_liquide:
                    x4 = (h4 - h4_liquide) / (h4_vapeur - h4_liquide)
                else:
                    x4 = 0.5
            except:
                x4 = 0.5  # Valeur par défaut

        # Calcul de la température t4 avec fallback pour mélanges
        t4_result = calculer_propriete(fluide, 'T', H=h4, P=p4)
        if t4_result is None:
            try:
                # Méthode alternative : utiliser le titre calculé
                t4_result = PropsSI('T', 'P', p4, 'Q', max(0, min(1, x4)), fluide)
            except:
                # Dernier recours : utiliser la température d'évaporation
                t4_result = to + 273.15

        t4 = t4_result - 273.15 if t4_result > 200 else t4_result

        # Point 5 : Sortie évaporateur (avec surchauffe utile uniquement)
        t5 = to + surchauffe_utile
        t5_k = t5 + 273.15
        h5 = calculer_propriete(fluide, 'H', T=t5_k, P=p0)

        if h5 is None:
            # Fallback: essayer avec vapeur saturée
            h5 = calculer_propriete(fluide, 'H', P=p0, Q=1)
            if h5 is None:
                st.error("Erreur lors du calcul de l'enthalpie au point 5")
                return None

        # Calculs de performance
        # Effet frigorifique = h5 - h4 (enthalpie sortie évaporateur - enthalpie entrée évaporateur)
        q_evap = h5 - h4
        q_cond = h2 - h3p
        w_comp = h2 - h1

        if q_evap <= 0:
            st.error("Erreur: L'effet frigorifique est négatif ou nul. Vérifiez vos paramètres.")
            return None

        # Débit massique
        if type_metrique == 'Volume balayé':
            vol_bal = valeur_metrique / 3600.0  # m³/h -> m³/s
            debit_massique = (vol_bal * rendement_vol) / v1 if v1 else 0
        else:
            puissance_frigo = valeur_metrique * 1000  # kW -> W
            debit_massique = puissance_frigo / q_evap if q_evap else 0

        # Puissances
        puissance_frigorifique = debit_massique * q_evap / 1000
        puissance_compression = debit_massique * w_comp / 1000
        puissance_condensation = debit_massique * q_cond / 1000

        # Volume balayé
        volume_balaye = (debit_massique * v1) / rendement_vol if v1 and rendement_vol > 0 else 0

        # Résultats
        resultats = {
            'points': {
                '0': {'T': to, 'P': p0/1e5, 'H': h5/1000, 'S': None, 'V': None, 'X': None},
                '1': {'T': t1, 'P': p1/1e5, 'H': h1/1000, 'S': s1/1000 if s1 else None, 'V': v1, 'X': None},
                '2is': {'T': t2is, 'P': p2/1e5, 'H': h2is/1000, 'S': s2is/1000 if s2is else None, 'V': None, 'X': None},
                '2': {'T': t2, 'P': p2/1e5, 'H': h2/1000, 'S': s2/1000 if s2 else None, 'V': None, 'X': None},
                '3': {'T': t3, 'P': p2/1e5, 'H': h3/1000, 'S': None, 'V': None, 'X': None},
                "3'": {'T': t3p, 'P': p3p/1e5, 'H': h3p/1000, 'S': None, 'V': None, 'X': None},
                '4': {'T': t4, 'P': p4/1e5, 'H': h4/1000, 'S': None, 'V': None, 'X': x4*100 if x4 is not None else None},
                '5': {'T': t5, 'P': p0/1e5, 'H': h5/1000, 'S': None, 'V': None, 'X': None}
            },
            'performance': {
                'debit_massique': debit_massique,
                'puissance_frigorifique': puissance_frigorifique,
                'puissance_compression': puissance_compression,
                'puissance_condensation': puissance_condensation,
                'volume_balaye': volume_balaye,
                'cop': puissance_frigorifique / puissance_compression if puissance_compression > 0 else 0
            }
        }

        return resultats

    except Exception as e:
        st.error(f"Erreur lors du calcul du cycle: {str(e)}")
        return None

def _compression_isentropique(fluide, s_aspiration, p_refoulement, t_ref_k, label):
    """Calcule h_is par PropsSI, avec bisection en secours pour les mélanges."""
    h_is = calculer_propriete(fluide, 'H', S=s_aspiration, P=p_refoulement)
    if h_is is None:
        t_low = t_ref_k + 5
        t_high = t_ref_k + 180
        for _ in range(40):
            t_est = (t_low + t_high) / 2
            try:
                s_est = PropsSI('S', 'P', p_refoulement, 'T', t_est, fluide)
                if abs(s_est - s_aspiration) < 0.5:
                    h_is = PropsSI('H', 'P', p_refoulement, 'T', t_est, fluide)
                    break
                if s_est < s_aspiration:
                    t_low = t_est
                else:
                    t_high = t_est
            except:
                break
        else:
            h_is = PropsSI('H', 'P', p_refoulement, 'T', (t_low + t_high) / 2, fluide)
    if h_is is None:
        raise ValueError(f"Impossible de calculer la compression isentropique {label}")
    return h_is


def generer_pdf_mono(resultats, fluide_lbl, schema_img_pil):
    """Génère un PDF multi-pages couleur pour le cycle mono-étagé."""
    import io
    from matplotlib.backends.backend_pdf import PdfPages

    perf   = resultats['performance']
    points = resultats['points']
    buf    = io.BytesIO()

    with PdfPages(buf) as pdf:

        # ── PAGE 1 : Schéma avec labels ──────────────────────────────────────
        fig1, ax1 = plt.subplots(figsize=(11.69, 8.27))
        fig1.patch.set_facecolor('white')
        ax1.axis('off')
        ax1.set_title(f'Schéma cycle mono-étagé  |  Fluide : {fluide_lbl}',
                      fontsize=14, fontweight='bold', color='#0f4c75', pad=10)
        if schema_img_pil:
            ax1.imshow(schema_img_pil)
        fig1.tight_layout(pad=0.5)
        pdf.savefig(fig1, dpi=150)
        plt.close(fig1)

        # ── PAGE 2 : Résultats de performance ────────────────────────────────
        fig2, ax2 = plt.subplots(figsize=(11.69, 8.27))
        fig2.patch.set_facecolor('white')
        ax2.axis('off')
        ax2.set_title(f'Résultats cycle mono-étagé  |  Fluide : {fluide_lbl}',
                      fontsize=14, fontweight='bold', color='#0f4c75', pad=10)
        vb = perf.get('volume_balaye', 0) * 3600
        qm = perf.get('debit_massique', 0) * 3600
        perf_rows = [
            ['Puissance frigorifique',  f"{perf.get('puissance_frigorifique', 0):.2f} kW"],
            ['Puissance de condensation', f"{perf.get('puissance_condensation', 0):.2f} kW"],
            ['Puissance de compression', f"{perf.get('puissance_compression', 0):.2f} kW"],
            ['COP',                     f"{perf.get('cop', 0):.3f}"],
            ['Débit massique',          f"{qm:.2f} kg/h"],
            ['Volume balayé',           f"{vb:.3f} m3/h"],
        ]
        tbl = ax2.table(
            cellText=perf_rows,
            colLabels=['Grandeur', 'Valeur'],
            cellLoc='left', loc='center',
            bbox=[0.1, 0.3, 0.8, 0.55]
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(12)
        for (row, col), cell in tbl.get_celld().items():
            if row == 0:
                cell.set_facecolor('#0f4c75')
                cell.set_text_props(color='white', fontweight='bold')
            elif row % 2 == 0:
                cell.set_facecolor('#f0f4f8')
            cell.set_edgecolor('#ccc')
        fig2.tight_layout(pad=0.5)
        pdf.savefig(fig2, dpi=150)
        plt.close(fig2)

        # ── PAGE 3 : Tableau des points du cycle ─────────────────────────────
        fig3, ax3 = plt.subplots(figsize=(11.69, 8.27))
        fig3.patch.set_facecolor('white')
        ax3.axis('off')
        ax3.set_title('Tableau des points du cycle', fontsize=14,
                      fontweight='bold', color='#0f4c75', pad=10)
        pt_labels = {'0': 'Évaporation (sat.)', '1': 'Aspiration compresseur',
                     '2is': 'Compression isentr.', '2': 'Refoulement compresseur',
                     '3': 'Condensation (sat.)', "3'": 'Sortie condenseur',
                     '4': 'Sortie détendeur', '5': 'Sortie évaporateur'}
        rows_pts = []
        for k, lbl in pt_labels.items():
            pt = points.get(k)
            if not pt:
                continue
            x_val = f"X={pt['X']:.1f}%" if pt.get('X') is not None else (
                     f"{pt['V']:.5f}" if pt.get('V') is not None else '—')
            rows_pts.append([f"{k} — {lbl}",
                f"{pt['T']:.2f}" if pt.get('T') is not None else '—',
                f"{pt['P']:.3f}" if pt.get('P') is not None else '—',
                f"{pt['H']:.2f}" if pt.get('H') is not None else '—',
                f"{pt['S']:.4f}" if pt.get('S') is not None else '—',
                x_val])
        tbl2 = ax3.table(
            cellText=rows_pts,
            colLabels=['Point', 'T [°C]', 'P [bar]', 'h [kJ/kg]', 's [kJ/kgK]', 'v / X'],
            cellLoc='left', loc='center',
            bbox=[0.0, 0.1, 1.0, 0.80]
        )
        tbl2.auto_set_font_size(False)
        tbl2.set_fontsize(10)
        for (row, col), cell in tbl2.get_celld().items():
            if row == 0:
                cell.set_facecolor('#263238')
                cell.set_text_props(color='white', fontweight='bold')
            elif row % 2 == 0:
                cell.set_facecolor('#f5f5f5')
            cell.set_edgecolor('#bbb')
        fig3.tight_layout(pad=0.3)
        pdf.savefig(fig3, dpi=150)
        plt.close(fig3)

        d = pdf.infodict()
        d['Title'] = f'Cycle mono-étagé — {fluide_lbl}'
        d['Author'] = 'CalcFlu'

    buf.seek(0)
    return buf


def generer_pdf_bietage(res, fluide_cp, schema_img_pil, fig_ph):
    """Génère un PDF multi-pages couleur pour le cycle bi-étagé."""
    import io
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.gridspec as gridspec

    perf  = res['performance']
    pts   = res['points']
    inter = res['intermediate']
    mode  = res.get('mode_original', res.get('mode', ''))
    fluide_lbl = res.get('fluide_affichage', '')

    buf = io.BytesIO()
    with PdfPages(buf) as pdf:

        # ── PAGE 1 : Schéma avec labels ──────────────────────────────────────
        fig1, ax1 = plt.subplots(figsize=(11.69, 8.27))  # A4 paysage
        fig1.patch.set_facecolor('white')
        ax1.axis('off')
        ax1.set_title(f'Schéma — {mode}  |  Fluide : {fluide_lbl}',
                      fontsize=14, fontweight='bold', color='#0f4c75', pad=10)
        if schema_img_pil:
            ax1.imshow(schema_img_pil, aspect='equal')
        fig1.tight_layout(pad=0.5)
        pdf.savefig(fig1, dpi=150)
        plt.close(fig1)

        # ── PAGE 2 : Résultats de performance ────────────────────────────────
        fig2, ax2 = plt.subplots(figsize=(11.69, 8.27))
        fig2.patch.set_facecolor('white')
        ax2.axis('off')
        ax2.set_title(f'Résultats — {mode}  |  Fluide : {fluide_lbl}',
                      fontsize=14, fontweight='bold', color='#0f4c75', pad=10)

        # Tableau de performance
        perf_rows = [
            ['Puissance frigo BP', f"{perf.get('q_evap_bp', perf['q_evap']):.2f} kW", '❄️'],
            ['Puissance frigo MP', f"{perf.get('q_evap_mp', 0):.2f} kW", '❄️'],
            ['Puissance frigo totale', f"{perf['q_evap']:.2f} kW", '❄️'],
            ['Puissance calorifique', f"{perf['q_cond']:.2f} kW", '🔥'],
            ['W compresseur BP',  f"{perf['w_bp']:.2f} kW",  '⚡'],
            ['W compresseur HP',  f"{perf['w_hp']:.2f} kW",  '⚡'],
            ['W total',           f"{perf['w_total']:.2f} kW",'⚡'],
            ['COP',               f"{perf['cop']:.3f}",       '🎯'],
            ['ṁ BP',  f"{perf['m_bp']*3600:.2f} kg/h",  '💧'],
            ['ṁ MP',  f"{perf.get('m_mp',0)*3600:.2f} kg/h", '💧'],
            ['ṁ HP',  f"{perf['m_hp']*3600:.2f} kg/h",  '💧'],
            ['Vb BP', f"{perf['v_bal_bp']:.3f} m³/h",   '📦'],
            ['Vb HP', f"{perf['v_bal_hp']:.3f} m³/h",   '📦'],
            ['pi',    f"{inter['p_int']:.3f} bar  |  ti = {inter['t_int']:.1f} °C", '🔀'],
            ['τ BP',  f"{perf['tau_bp']:.2f}",  ''],
            ['τ HP',  f"{perf['tau_hp']:.2f}",  ''],
            ['r = ṁHP/ṁBP', f"{perf['r']:.4f}", ''],
        ]
        col_labels = ['Grandeur', 'Valeur', '']
        col_colors = [['#e3f2fd', '#e8f5e9', '#fff'] for _ in perf_rows]
        tbl = ax2.table(
            cellText=[[r[0], r[1]] for r in perf_rows],
            colLabels=['Grandeur', 'Valeur'],
            cellLoc='left', loc='center',
            bbox=[0.05, 0.05, 0.9, 0.88]
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(10)
        for (row, col), cell in tbl.get_celld().items():
            if row == 0:
                cell.set_facecolor('#0f4c75')
                cell.set_text_props(color='white', fontweight='bold')
            elif row % 2 == 0:
                cell.set_facecolor('#f0f4f8')
            cell.set_edgecolor('#ccc')
        fig2.tight_layout(pad=0.5)
        pdf.savefig(fig2, dpi=150)
        plt.close(fig2)

        # ── PAGE 3 : Tableau des points du cycle ─────────────────────────────
        fig3, ax3 = plt.subplots(figsize=(11.69, 8.27))
        fig3.patch.set_facecolor('white')
        ax3.axis('off')
        ax3.set_title('Tableau des points du cycle', fontsize=14,
                      fontweight='bold', color='#0f4c75', pad=10)

        pt_labels = {
            '1':'Aspiration BP','2is':'Compression BP (isentr.)','2':'Refoulement BP',
            '3':'Aspiration HP','4is':'Compression HP (isentr.)','4':'Refoulement HP',
            '5':'Sortie condenseur','6':'Sortie détendeur pi','7':'Entrée déten. BP',
            '8':'Sortie déten. BP','9':'Sortie évap BP','10':'Sortie HX MP','11':'Sortie évap MP',
        }
        rows_pts = []
        for k, lbl in pt_labels.items():
            pt = pts.get(k)
            if not pt:
                continue
            x_val = f"X={pt['X']:.1f}%" if pt.get('X') is not None else (
                     f"{pt['V']:.5f} m³/kg" if pt.get('V') is not None else '—')
            rows_pts.append([
                f"{k} — {lbl}",
                f"{pt['T']:.2f}" if pt.get('T') is not None else '—',
                f"{pt['P']:.3f}" if pt.get('P') is not None else '—',
                f"{pt['H']:.2f}" if pt.get('H') is not None else '—',
                f"{pt['S']:.4f}" if pt.get('S') is not None else '—',
                x_val,
            ])
        tbl2 = ax3.table(
            cellText=rows_pts,
            colLabels=['Point', 'T [°C]', 'P [bar]', 'h [kJ/kg]', 's [kJ/kgK]', 'v / X'],
            cellLoc='left', loc='center',
            bbox=[0.0, 0.0, 1.0, 0.92]
        )
        tbl2.auto_set_font_size(False)
        tbl2.set_fontsize(9)
        for (row, col), cell in tbl2.get_celld().items():
            if row == 0:
                cell.set_facecolor('#263238')
                cell.set_text_props(color='white', fontweight='bold')
            elif row % 2 == 0:
                cell.set_facecolor('#f5f5f5')
            cell.set_edgecolor('#bbb')
        fig3.tight_layout(pad=0.3)
        pdf.savefig(fig3, dpi=150)
        plt.close(fig3)

        # ── PAGE 4 : Diagramme P-h ───────────────────────────────────────────
        if fig_ph:
            pdf.savefig(fig_ph, dpi=150)

        # Métadonnées
        d = pdf.infodict()
        d['Title'] = f'Cycle bi-étagé — {mode} — {fluide_lbl}'
        d['Author'] = 'CalcFlu'

    buf.seek(0)
    return buf


def _charger_police(taille):
    """Charge une police bold disponible sur Windows et Linux (Streamlit Cloud)."""
    from PIL import ImageFont
    candidates = [
        "arialbd.ttf",                                                    # Windows
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",          # Ubuntu/Debian
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # CentOS/RHEL
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",                   # autre Linux
        "DejaVuSans-Bold.ttf",
        "LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, taille)
        except Exception:
            continue
    # Dernier recours : load_default avec taille (Pillow >= 10)
    try:
        return ImageFont.load_default(size=taille)
    except Exception:
        return ImageFont.load_default()


def superposer_schema_mono(img_path, perf, fluide_lbl=''):
    """Surimpression des résultats sur circuitFrigo.png (770×477 px)."""
    from PIL import ImageDraw, ImageFont
    raw = Image.open(img_path)
    bg = Image.new('RGB', raw.size, (255, 255, 255))
    if raw.mode in ('RGBA', 'LA') or (raw.mode == 'P' and 'transparency' in raw.info):
        bg.paste(raw, mask=raw.convert('RGBA').split()[3])
    else:
        bg.paste(raw)
    img = bg
    draw = ImageDraw.Draw(img)

    font_bold = _charger_police(22)

    vb   = perf.get('volume_balaye', 0) * 3600  # m³/s → m³/h
    qm   = perf.get('debit_massique', 0) * 3600  # kg/s → kg/h
    phik = perf.get('puissance_condensation', 0)
    phi0 = perf.get('puissance_frigorifique', 0)

    # (x, y, texte, couleur) — coin supérieur gauche, image 770×477 px
    zones = [
        (344, 129, f"{vb:.2f} m3/h",    '#7b1fa2'),  # Vb
        (266, 382, f"{qm:.1f} kg/h",     '#1565c0'),  # qm
        (654, 223, f"{phik:.1f} kW",     '#e65100'),  # Phi k
        ( 82, 244, f"{phi0:.1f} kW",     '#1976d2'),  # Phi 0
        (330, 204, fluide_lbl,           '#2e7d32'),  # Fluide
    ]

    for (x, y, txt, col) in zones:
        if txt:
            draw.text((x, y), txt, fill=col, font=font_bold)

    return img


def superposer_volumes_schema(img_path, perf):
    """Superpose les résultats sur le schéma aux positions des cadres."""
    from PIL import ImageDraw, ImageFont
    raw = Image.open(img_path)
    bg = Image.new('RGB', raw.size, (255, 255, 255))
    if raw.mode in ('RGBA', 'LA') or (raw.mode == 'P' and 'transparency' in raw.info):
        bg.paste(raw, mask=raw.convert('RGBA').split()[3])
    else:
        bg.paste(raw)
    img = bg
    w, h = img.size
    draw = ImageDraw.Draw(img)

    font_bold = _charger_police(max(28, int(w * 0.025)))

    # (coin_sup_gauche_x, coin_sup_gauche_y, texte, couleur)
    # Coordonnées = pixel / taille image (2219 x 2838)
    zones = [
        (495.4/2219,  279.1/2838, f"{perf['v_bal_bp']:.2f} m3/h",           '#7b1fa2'),  # Vb BP
        (1327 /2219,  279.1/2838, f"{perf['v_bal_hp']:.2f} m3/h",           '#c62828'),  # Vb HP
        (417.1/2219,  494.6/2838, f"{perf.get('q_evap_mp', 0):.1f} kW",    '#1565c0'),  # φ MP
        (1806 /2219,  676  /2838, f"{perf['q_cond']:.1f} kW",              '#e65100'),  # Phi k
        (1264 /2219,  1071 /2838, f"{perf['m_hp']*3600:.1f} kg/h",         '#c62828'),  # qm HP
        (755  /2219,  1521 /2838, f"{perf['m_bp']*3600:.1f} kg/h",         '#7b1fa2'),  # qm BP
        (118  /2219,  1752 /2838, f"{perf.get('q_evap_bp', perf['q_evap']):.1f} kW", '#1976d2'),  # Phi 0 BP
    ]

    for (rx, ry, txt, col) in zones:
        x = int(w * rx)
        y = int(h * ry)
        draw.text((x, y), txt, fill=col, font=font_bold)

    return img


def superposer_schema_inj_partielle(img_path, perf):
    """Surimpression des résultats sur schemaFluInjPartielleEcgPlaque.png (2221×1292 px)."""
    from PIL import ImageDraw, ImageFont
    raw = Image.open(img_path)
    bg = Image.new('RGB', raw.size, (255, 255, 255))
    if raw.mode in ('RGBA', 'LA') or (raw.mode == 'P' and 'transparency' in raw.info):
        bg.paste(raw, mask=raw.convert('RGBA').split()[3])
    else:
        bg.paste(raw)
    img = bg
    w, h = img.size   # 2221 × 1292
    draw = ImageDraw.Draw(img)

    font_bold = _charger_police(max(28, int(w * 0.025)))

    # Coordonnées coin supérieur gauche — image 2221×1292 px
    _qm_inj = (perf['m_hp'] - perf['m_bp']) * 3600  # ṁ_inj = ṁ_HP − ṁ_BP
    zones = [
        ( 230, 260, f"{perf['v_bal_bp']:.2f} m3/h",                         '#7b1fa2'),  # Vb BP
        (1410, 260, f"{perf['v_bal_hp']:.2f} m3/h",                         '#c62828'),  # Vb HP
        (1838, 762, f"{perf['q_cond']:.1f} kW",                            '#e65100'),  # Phi k
        (1467,1234, f"{perf['m_hp']*3600:.1f} kg/h",                       '#c62828'),  # qm HP
        (1170, 472, f"{perf['m_bp']*3600:.1f} kg/h",                       '#7b1fa2'),  # qm BP
        ( 613, 536, f"{_qm_inj:.1f} kg/h",                                 '#2e7d32'),  # qm MP (injection)
        ( 117, 622, f"{perf.get('q_evap_bp', perf['q_evap']):.1f} kW",     '#1976d2'),  # Phi 0 BP
    ]

    for (px, py, txt, col) in zones:
        draw.text((px, py), txt, fill=col, font=font_bold)

    return img


def superposer_schema_bouteille_bp(img_path, perf):
    """Surimpression des résultats sur schemaFluBiEtageInjTotalePompeEcHPlaque.png (4134×2243 px)."""
    from PIL import ImageDraw, ImageFont
    raw = Image.open(img_path)
    bg = Image.new('RGB', raw.size, (255, 255, 255))
    if raw.mode in ('RGBA', 'LA') or (raw.mode == 'P' and 'transparency' in raw.info):
        bg.paste(raw, mask=raw.convert('RGBA').split()[3])
    else:
        bg.paste(raw)
    img = bg
    w, h = img.size   # 4134 × 2243
    draw = ImageDraw.Draw(img)

    font_bold = _charger_police(max(40, int(w * 0.015)))

    # Coordonnées dans l'espace 4134×2443 → y corrigé ×(2243/2443)
    _sy = 2243 / 2443.0
    _m_mp = perf.get('m_mp', 0.0)
    zones = [
        (2400, int( 279 * _sy), f"{perf['v_bal_bp']:.2f} m3/h",                         '#7b1fa2'),  # Vb BP
        (3267, int( 279 * _sy), f"{perf['v_bal_hp']:.2f} m3/h",                         '#c62828'),  # Vb HP
        (3762, int( 660 * _sy) + 40, f"{perf['q_cond']:.1f} kW",                            '#e65100'),  # Phi k
        (3387, int(1336 * _sy) +100, f"{perf['m_hp']*3600:.1f} kg/h",                       '#c62828'),  # qm HP
        (2114, int(1603 * _sy) +160, f"{perf['m_bp']*3600:.1f} kg/h",                       '#7b1fa2'),  # qm BP
        (2389, int( 870 * _sy) +110, f"{perf.get('q_evap_mp', 0):.1f} kW",                  '#1565c0'),  # Phi 0 MP
        ( 183, int(1585 * _sy) +170, f"{perf.get('q_evap_bp', perf['q_evap']):.1f} kW",     '#1976d2'),  # Phi 0 BP
        (2423, int(1486 * _sy) +100, f"{_m_mp*3600:.1f} kg/h" if _m_mp > 0 else "--- kg/h", '#2e7d32'),  # qm MP
    ]

    for (px, py, txt, col) in zones:
        draw.text((px, py), txt, fill=col, font=font_bold)

    return img


def tracer_ph_bietage(res, fluide_cp):
    """Génère le diagramme P-h du cycle bi-étagé (matplotlib, petit format)."""
    pts  = res['points']
    perf = res['performance']
    mode = res.get('mode', 'Injection totale')

    # ── Dôme de saturation ──────────────────────────────────────────────────
    try:
        t_crit = PropsSI('Tcrit', fluide_cp)
        p_crit = PropsSI('Pcrit', fluide_cp)
        t_min  = max(PropsSI('Tmin', fluide_cp), 180.0)
        temps  = np.linspace(t_min, t_crit * 0.9999, 300)
        h_liq  = [PropsSI('H', 'T', t, 'Q', 0, fluide_cp) / 1000 for t in temps]
        h_vap  = [PropsSI('H', 'T', t, 'Q', 1, fluide_cp) / 1000 for t in temps]
        p_sat  = [PropsSI('P', 'T', t, 'Q', 0, fluide_cp) / 1e5  for t in temps]
        h_crit = PropsSI('H', 'T', t_crit, 'Q', 0.5, fluide_cp) / 1000
        p_crit_bar = p_crit / 1e5
    except Exception:
        return None

    fig, ax = plt.subplots(figsize=(5, 3.5))
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#f8fafc')

    # Dôme
    ax.plot(h_liq, p_sat, color='#1565c0', lw=1.2)
    ax.plot(h_vap, p_sat, color='#1565c0', lw=1.2)
    ax.plot(h_crit, p_crit_bar, 'o', color='#1565c0', ms=3)

    def h(pt): return pts[pt]['H']
    def p(pt): return pts[pt]['P']

    p0  = p('1');  pi = p('2');  pk = p('4')

    # ── Tracé du cycle ───────────────────────────────────────────────────────
    # Compression BP  1→2is (tiret) + 1→2 (plein)
    ax.plot([h('1'), h('2is')], [p0, pi],  '--', color='#9c27b0', lw=0.9, alpha=0.6)
    ax.plot([h('1'), h('2')],   [p0, pi],  color='#9c27b0', lw=1.4)
    # Mélange / bouteille  2→3  (pointillé)
    ax.plot([h('2'), h('3')],   [pi, pi],  ':', color='#ff9800', lw=1.2)
    # Compression HP  3→4is (tiret) + 3→4 (plein)
    ax.plot([h('3'), h('4is')], [pi, pk],  '--', color='#e53935', lw=0.9, alpha=0.6)
    ax.plot([h('3'), h('4')],   [pi, pk],  color='#e53935', lw=1.4)
    # Condensation  4→5
    ax.plot([h('4'), h('5')],   [pk, pk],  color='#e53935', lw=1.4)
    # 1er détendeur  5→6  (pk→pi)
    ax.plot([h('5'), h('6')],   [pk, pi],  color='#00897b', lw=1.2)
    # Point 7 : à pi pour injection totale, à pk pour injection partielle (après échangeur)
    ax.plot([h('7')], [p('7')], 'o', color='#00897b', ms=4)
    # Injection partielle : sous-refroidissement HX 5→7 à pk + échangeur 6→10 à pi
    if mode == 'Injection partielle':
        ax.plot([h('5'), h('7')], [pk, pk], color='#1565c0', lw=1.2, ls='--')
        if '10' in pts and pts['10']['H'] is not None:
            ax.plot([h('6'), pts['10']['H']], [pi, pts['10']['P']], color='#ff6f00', lw=1.2)
            ax.plot([pts['10']['H'], h('3')], [pts['10']['P'], pi], color='#ff6f00', lw=1.2, ls='--')
    # 2ème détendeur → p0 (depuis p('7') qui est correct selon le mode)
    if mode in ('Injection totale', 'Injection partielle'):
        ax.plot([h('7'), h('8')], [p('7'), p0], color='#00897b', lw=1.2)
    else:  # EVI
        ax.plot([h('5'), h('8')], [pk, p0], color='#00897b', lw=1.2)
    # Évaporation  8→1
    ax.plot([h('8'), h('1')],   [p0, p0],  color='#1976d2', lw=1.4)

    # ── Lignes isobares de référence ─────────────────────────────────────────
    all_h = [pts[k]['H'] for k in pts] + h_liq + h_vap
    h_min = min(all_h)
    for pbar, lbl, col in [(p0, f'p₀={p0:.2f}b', '#1976d2'),
                            (pi, f'pi={pi:.2f}b', '#00897b'),
                            (pk, f'pₖ={pk:.2f}b', '#e53935')]:
        ax.axhline(pbar, color=col, lw=0.5, ls='--', alpha=0.4)
        ax.text(h_min, pbar, f' {lbl}', va='bottom', fontsize=6, color=col, alpha=0.7)

    # ── Pompe MP : points 10 et 11 ──────────────────────────────────────────
    has_mp_pts = ('10' in pts and '11' in pts and
                  pts['10']['H'] is not None and pts['11']['H'] is not None)
    if has_mp_pts:
        h10v = pts['10']['H']; p10v = pts['10']['P']
        h11v = pts['11']['H']; p11v = pts['11']['P']
        # 7→10 : pompe (compression liquide)
        ax.annotate('', xy=(h10v, p10v), xytext=(h('7'), pi),
                    arrowprops=dict(arrowstyle='->', color='#4a235a', lw=1.4,
                                   mutation_scale=10), zorder=5)
        ax.plot([h('7'), h10v], [pi, p10v], color='#4a235a', lw=1.4)
        # 10→11 : évaporation MP (de pi+dp à pi, quasi-horizontale)
        ax.plot([h10v, h11v], [p10v, p11v], color='#ff6f00', lw=1.4, zorder=4)
        ax.annotate('', xy=(h11v, p11v), xytext=(h10v + (h11v-h10v)*0.5, (p10v+p11v)/2),
                    arrowprops=dict(arrowstyle='->', color='#ff6f00', lw=1.4,
                                   mutation_scale=10), zorder=5)

    # ── Numérotation des points ──────────────────────────────────────────────
    shown = {'1': (h('1'), p0),    '2': (h('2'), pi),   '3': (h('3'), pi),
             '4': (h('4'), pk),    '5': (h('5'), pk),   '6': (h('6'), pi),
             '7': (h('7'), p('7')), '8': (h('8'), p0)}
    offsets = {'1': (-6, -8), '2': (3, 3), '3': (-8, 3), '4': (3, 3),
               '5': (3, -8), '6': (3, 3), '7': (-8, -8), '8': (3, -8)}
    if has_mp_pts:
        shown['10'] = (pts['10']['H'], pts['10']['P'])
        shown['11'] = (pts['11']['H'], pts['11']['P'])
        offsets['10'] = (3, -8)
        offsets['11'] = (3, 3)
    # Points 9 et 10 injection partielle — indépendants de la pompe
    if mode == 'Injection partielle':
        if '9'  in pts and pts['9']['H']  is not None:
            shown['9']  = (pts['9']['H'],  pts['9']['P'])
            offsets['9'] = (-8, -8)
        if '10' in pts and pts['10']['H'] is not None:
            shown['10'] = (pts['10']['H'], pts['10']['P'])
            offsets['10'] = (3, 3)
    for lbl, (hv, pv) in shown.items():
        ax.plot(hv, pv, 'o', color='#333', ms=3.5, zorder=6)
        dx, dy = offsets.get(lbl, (3, 3))
        ax.annotate(lbl, (hv, pv), xytext=(dx, dy), textcoords='offset points',
                    fontsize=7, color='#222', fontweight='bold')

    ax.set_yscale('log')
    ax.set_xlabel('h  [kJ/kg]', fontsize=8)
    ax.set_ylabel('P  [bar]',   fontsize=8)
    ax.set_title(f'Diagramme P-h — {mode}', fontsize=8, pad=4)
    ax.tick_params(labelsize=7)
    ax.grid(True, which='both', ls=':', lw=0.4, alpha=0.5)
    plt.tight_layout(pad=0.8)
    return fig


def tracer_schema_bietage(mode='Injection totale'):
    """Schéma de principe de l'installation bi-étagée (matplotlib)."""
    from matplotlib.patches import FancyBboxPatch
    from matplotlib.lines import Line2D

    fig, ax = plt.subplots(figsize=(5.0, 6.5))
    fig.patch.set_facecolor('#f0f4f8')
    ax.set_facecolor('#f0f4f8')
    ax.set_xlim(0, 10)
    ax.set_ylim(-1.2, 11.2)
    ax.axis('off')

    def box(x, y, w, h, lines, fc, fontsize=7.5):
        r = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                           facecolor=fc, edgecolor='#333', lw=1.2, zorder=3)
        ax.add_patch(r)
        if isinstance(lines, str):
            lines = [lines]
        n = len(lines)
        for i, ln in enumerate(lines):
            yy = y + h / 2 + (n - 1 - 2 * i) * 0.22
            ax.text(x + w / 2, yy, ln, ha='center', va='center',
                    fontsize=fontsize, fontweight='bold', color='white', zorder=4)

    def pipe(xs, ys, color, lw=1.6):
        ax.plot(xs, ys, '-', color=color, lw=lw,
                solid_capstyle='round', solid_joinstyle='round', zorder=2)
        # flèche au 2/3 du segment le plus long
        segs = [(abs(xs[i+1]-xs[i]) + abs(ys[i+1]-ys[i]), i) for i in range(len(xs)-1)]
        _, idx = max(segs)
        mx = (xs[idx] + xs[idx+1]) / 2
        my = (ys[idx] + ys[idx+1]) / 2
        dx = xs[idx+1] - xs[idx]
        dy = ys[idx+1] - ys[idx]
        norm = (dx**2 + dy**2) ** 0.5 or 1
        ax.annotate('', xy=(mx + dx/norm*0.01, my + dy/norm*0.01),
                    xytext=(mx - dx/norm*0.01, my - dy/norm*0.01),
                    arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                   mutation_scale=12), zorder=5)

    def dot(x, y, label):
        ax.plot(x, y, 'o', color='white', ms=11, zorder=7,
                markeredgecolor='#333', markeredgewidth=1.2)
        ax.text(x, y, label, ha='center', va='center',
                fontsize=7, fontweight='bold', color='#111', zorder=8)

    # ── Équipements ───────────────────────────────────────────────────────
    box(1.0, 9.0, 8.0, 1.0, 'CONDENSEUR',           '#1565c0', fontsize=8.5)
    box(0.2, 6.0, 2.6, 1.3, ['COMP.', 'HP'],        '#7b1fa2')
    box(7.2, 6.0, 2.6, 1.3, ['DÉT. 1', '→ pi'],    '#00897b')
    box(3.5, 3.5, 3.0, 2.0, ['BOUTEILLE', 'INTERMÉD.'], '#e65100')
    box(0.2, 1.2, 2.6, 1.3, ['COMP.', 'BP'],        '#9c27b0')
    box(7.2, 1.2, 2.6, 1.3, ['DÉT. 2', '→ p₀'],    '#00897b')
    box(1.0, 0.0, 8.0, 0.9, 'ÉVAPORATEUR',          '#1976d2', fontsize=8.5)

    # ── Tuyauteries ───────────────────────────────────────────────────────
    # 4 : Refoul. HP → Condenseur
    pipe([1.5, 1.5, 2.0], [7.3, 9.2, 9.2], '#e53935')
    dot(1.5, 7.3, '4')

    # 5 : Condenseur → Dét. 1
    pipe([8.0, 8.5, 8.5], [9.0, 9.0, 7.3], '#64b5f6')
    dot(8.5, 7.5, '5')

    # 6 : Dét. 1 → Bouteille
    pipe([8.5, 8.5, 6.5], [6.0, 5.2, 5.2], '#00897b')
    dot(8.5, 5.8, '6')

    if mode == 'Injection totale':
        # 3 : Bouteille (vapeur sat.) → Comp HP
        pipe([4.5, 4.5, 1.5, 1.5], [5.5, 6.6, 6.6, 6.0], '#ffb300')
        dot(1.5, 6.2, '3')
        # 7 : Bouteille (liquide sat.) → Dét. 2
        pipe([5.5, 5.5, 8.5, 8.5], [3.5, 3.1, 3.1, 2.5], '#00695c')
        dot(5.5, 3.5, '7')
        # 2 : Refoul. BP → Bouteille
        pipe([1.5, 1.5, 3.5], [2.5, 4.2, 4.2], '#ce93d8')
        dot(1.5, 2.5, '2')
        ax.text(3.0, 4.35, '↑ mélange', fontsize=6, color='#9c27b0',
                ha='center', style='italic')
    elif mode == 'Injection partielle':
        # 3 : Bouteille (vapeur) injectée sur conduite aspi HP
        pipe([4.5, 4.5, 2.8, 2.8, 1.5, 1.5], [5.5, 6.8, 6.8, 6.6, 6.6, 6.0], '#ffb300')
        dot(1.5, 6.2, '3')
        # Injection en point 2 (après comp BP, avant HP)
        pipe([1.5, 1.5, 2.8], [2.5, 3.2, 3.2], '#ce93d8')
        dot(1.5, 2.5, '2')
        ax.annotate('', xy=(2.8, 6.6), xytext=(2.8, 3.2),
                    arrowprops=dict(arrowstyle='->', color='#00897b', lw=1.3))
        ax.text(3.05, 5.0, 'injection', fontsize=5.5, color='#00897b',
                ha='left', style='italic', rotation=90)
        # Liquide direct condenseur → dét 2
        pipe([5.5, 5.5, 8.5, 8.5], [3.5, 3.1, 3.1, 2.5], '#00695c')
        dot(5.5, 3.5, '7')
    else:  # EVI
        # EVI: ligne tiretée de l'échangeur
        pipe([4.5, 4.5, 1.5, 1.5], [5.5, 6.6, 6.6, 6.0], '#ffb300')
        dot(1.5, 6.2, '3')
        pipe([5.5, 5.5, 8.5, 8.5], [3.5, 3.1, 3.1, 2.5], '#00695c')
        dot(5.5, 3.5, '7')
        pipe([1.5, 1.5, 3.5], [2.5, 4.2, 4.2], '#ce93d8')
        dot(1.5, 2.5, '2')
        ax.text(5.0, 5.6, 'EVI\n(échangeur)', fontsize=6.5, color='#00897b',
                ha='center', va='center', style='italic',
                bbox=dict(boxstyle='round,pad=0.3', fc='#e0f2f1', ec='#00897b', lw=1))

    # 8 : Dét. 2 → Évap.
    pipe([8.5, 8.5, 8.0], [1.2, 0.65, 0.65], '#42a5f5')
    dot(8.5, 1.6, '8')

    # 1 : Évap. → Comp BP
    pipe([2.0, 1.5, 1.5], [0.45, 0.45, 1.2], '#7986cb')
    dot(2.2, 0.45, '1')

    # ── Légende ───────────────────────────────────────────────────────────
    legend_elements = [
        Line2D([0], [0], color='#e53935', lw=1.5, label='Gaz chaud HP'),
        Line2D([0], [0], color='#64b5f6', lw=1.5, label='Liquide HP'),
        Line2D([0], [0], color='#ffb300', lw=1.5, label='Vap. sat. pi'),
        Line2D([0], [0], color='#00695c', lw=1.5, label='Liq. sat. pi'),
        Line2D([0], [0], color='#7986cb', lw=1.5, label='Vapeur BP'),
    ]
    ax.legend(handles=legend_elements, loc='lower center', ncol=3,
              fontsize=6, framealpha=0.85, bbox_to_anchor=(0.5, -0.14),
              edgecolor='#ccc')

    mode_colors = {'Injection totale': '#e65100',
                   'Injection partielle': '#1565c0',
                   'Sous-refroidisseur (EVI)': '#00695c'}
    ax.set_title(f'Schéma — {mode}', fontsize=8.5, fontweight='bold',
                 color=mode_colors.get(mode, '#333'), pad=5)

    plt.tight_layout(pad=0.5)
    return fig


def calculer_cycle_bietage():
    """Cycle bi-étagé — trois architectures d'intercooling :
      - Injection totale  : bouteille intermédiaire, tout le liquide passe par pi
      - Injection partielle : désurchauffe du refoulement BP par injection de liquide à pi
      - Sous-refroidisseur (EVI) : échangeur économiseur qui sous-refroidit le liquide principal
    """
    mode_original = st.session_state.get('bi_mode', 'Injection totale')
    mode          = mode_original
    # "Injection totale avec bouteille BP" utilise le même calcul que "Injection totale"
    if mode == 'Injection totale avec bouteille BP':
        mode = 'Injection totale'
    has_pump     = st.session_state.get('bi_has_pump', False)
    pump_n       = st.session_state.get('bi_pump_n', 3.0) or 3.0
    pump_dp      = st.session_state.get('bi_pump_dp', 0.5) or 0.5
    pump_eta     = st.session_state.get('bi_pump_eta', 0.60) or 0.60
    pump_height  = st.session_state.get('bi_pump_height', 2.0) or 2.0
    dt_sub_hx    = st.session_state.get('bi_dt_sub_hx', 5.0) or 5.0
    dt_pincement        = st.session_state.get('bi_dt_pincement', 5.0) or 5.0
    surchauffe_evap_bp  = st.session_state.get('bi_surchauffe_evap_bp', 5.0) or 5.0

    fluide_affichage = st.session_state.get('bi_fluide', FLUIDES[0])
    fluide = obtenir_fluide_coolprop(fluide_affichage)

    to  = st.session_state.get('bi_to')
    po  = st.session_state.get('bi_po')
    # En injection partielle, utiliser bi_surchauffe_evap_bp pour la surchauffe BP (unique saisie)
    if mode_original == 'Injection partielle':
        surchauffe = st.session_state.get('bi_surchauffe_evap_bp', 5.0) or 5.0
    else:
        surchauffe = st.session_state.get('bi_surchauffe', 5.0) or 5.0
    tc  = st.session_state.get('bi_tc')
    pk  = st.session_state.get('bi_pk')
    sous_refroid = st.session_state.get('bi_sous_refroid', 5.0) or 5.0
    pi_mode = st.session_state.get('bi_pi_mode', 'Auto (√(p₀×pₖ))')
    ti      = st.session_state.get('bi_ti')
    pi_bar  = st.session_state.get('bi_pi')

    eta_vol_bp = st.session_state.get('bi_eta_vol_bp', 0.78) or 0.78
    eta_is_bp  = st.session_state.get('bi_eta_is_bp',  0.75) or 0.75
    eta_vol_hp = st.session_state.get('bi_eta_vol_hp', 0.78) or 0.78
    eta_is_hp  = st.session_state.get('bi_eta_is_hp',  0.75) or 0.75

    type_entree   = st.session_state.get('bi_type_entree', 'Puissance frigorifique [kW]')
    valeur_entree = st.session_state.get('bi_valeur_entree', 0.0)
    q_evap_mp     = st.session_state.get('bi_q_evap_mp', 0.0) or 0.0

    if not valeur_entree or valeur_entree <= 0:
        st.error("Veuillez entrer une valeur valide (puissance ou volume balayé BP)")
        return None

    try:
        # ── PRESSIONS ────────────────────────────────────────────────────────
        if po is not None and po > 0:
            p0 = po * 1e5
            for q in [1, 0.5, 0]:
                try:
                    t0_k = PropsSI('T', 'P', p0, 'Q', q, fluide)
                    if t0_k: break
                except: continue
            to = t0_k - 273.15
        elif to is not None:
            t0_k = to + 273.15
            for q in [1, 0.5, 0]:
                try:
                    p0 = PropsSI('P', 'T', t0_k, 'Q', q, fluide)
                    if p0: break
                except: continue
        else:
            st.error("Entrez la température ou la pression d'évaporation")
            return None

        if pk is not None and pk > 0:
            p_k = pk * 1e5
            for q in [0, 0.5, 1]:
                try:
                    tc_k = PropsSI('T', 'P', p_k, 'Q', q, fluide)
                    if tc_k: break
                except: continue
            tc = tc_k - 273.15
        elif tc is not None:
            tc_k = tc + 273.15
            for q in [0, 0.5, 1]:
                try:
                    p_k = PropsSI('P', 'T', tc_k, 'Q', q, fluide)
                    if p_k: break
                except: continue
        else:
            st.error("Entrez la température ou la pression de condensation")
            return None

        if pi_mode == 'Auto (√(p₀×pₖ))':
            p_i = (p0 * p_k) ** 0.5
        elif pi_bar is not None and pi_bar > 0:
            p_i = pi_bar * 1e5
        elif ti is not None:
            ti_k = ti + 273.15
            for q in [0, 0.5, 1]:
                try:
                    p_i = PropsSI('P', 'T', ti_k, 'Q', q, fluide)
                    if p_i: break
                except: continue
        else:
            p_i = (p0 * p_k) ** 0.5

        if not (p0 < p_i < p_k):
            st.error(f"pi ({p_i/1e5:.3f} bar) doit être strictement entre p₀ ({p0/1e5:.3f} bar) et pₖ ({p_k/1e5:.3f} bar)")
            return None

        p_int_bar = p_i / 1e5

        # ── PROPRIÉTÉS À pi ──────────────────────────────────────────────────
        t_int_k   = PropsSI('T', 'P', p_i, 'Q', 0, fluide)
        t_int     = t_int_k - 273.15
        h_liq_int = PropsSI('H', 'P', p_i, 'Q', 0, fluide)
        h_vap_int = PropsSI('H', 'P', p_i, 'Q', 1, fluide)
        s_vap_int = PropsSI('S', 'P', p_i, 'Q', 1, fluide)
        v_vap_int = 1.0 / PropsSI('D', 'P', p_i, 'Q', 1, fluide)

        # ── POINT 1 : aspiration BP ──────────────────────────────────────────
        t1   = to + surchauffe
        h1   = PropsSI('H', 'T', t1 + 273.15, 'P', p0, fluide)
        s1   = PropsSI('S', 'T', t1 + 273.15, 'P', p0, fluide)
        v1   = 1.0 / PropsSI('D', 'T', t1 + 273.15, 'P', p0, fluide)

        # ── POINT 2 : refoulement BP ─────────────────────────────────────────
        h2is = _compression_isentropique(fluide, s1, p_i, t_int_k, 'BP')
        t2is_r = calculer_propriete(fluide, 'T', H=h2is, P=p_i)
        t2is = (t2is_r - 273.15) if t2is_r else t_int + 30
        h2   = h1 + (h2is - h1) / eta_is_bp
        t2_r = calculer_propriete(fluide, 'T', H=h2, P=p_i)
        t2   = (t2_r - 273.15) if t2_r else t_int + 50
        s2   = calculer_propriete(fluide, 'S', H=h2, P=p_i)

        # ── POINT 5 : sortie condenseur ──────────────────────────────────────
        t5 = tc - sous_refroid
        h5 = PropsSI('H', 'T', t5 + 273.15, 'P', p_k, fluide)

        # ── BILAN MASSIQUE selon le mode ─────────────────────────────────────
        h0_liq = PropsSI('H', 'P', p0, 'Q', 0, fluide)
        h0_vap = PropsSI('H', 'P', p0, 'Q', 1, fluide)

        if mode == 'Injection totale':
            # Bouteille intermédiaire idéale
            denom = h_vap_int - h5
            if abs(denom) < 10.0:
                st.error("h''_int ≈ h5 : pi trop proche de pk")
                return None
            h3 = h_vap_int
            s3 = s_vap_int
            t3 = t_int
            # Point 6 : h5 → pi (flash)
            h6 = h5
            x6 = (h5 - h_liq_int) / (h_vap_int - h_liq_int) if (h_vap_int - h_liq_int) > 0 else 0
            # Point 7 : liq sat à pi (h'_int)
            h7 = h_liq_int
            # Point 8 : h7 → p0 (détente BP)
            h8 = h_liq_int
            x8 = (h8 - h0_liq) / (h0_vap - h0_liq) if (h0_vap - h0_liq) > 0 else 0
            # Débit MP (évaporateur intermédiaire à pi)
            _dh_int = h_vap_int - h_liq_int
            # r et m_HP calculés APRÈS m_BP (voir section débits)
            _has_mp_evap = (q_evap_mp > 0)
            bilan_str = f"ṁ_HP = [ṁ_BP×(h₂−h′) + ṁ_MP×(h″−h′)] / (h″−h₅)"

        elif mode == 'Injection partielle':
            # Injection partielle avec échangeur intermédiaire :
            # Le liquide condenseur est sous-refroidi par l'échangeur avant le détendeur BP
            # h7 = liquide sous-refroidi (après échangeur) → h8 = h7 (isenthalpique)
            # Bilan échangeur : ṁ_inj / ṁ_BP = (h5 − h7) / (h″_int − h′_int)
            # r = 1 + (h5 − h7) / (h″_int − h′_int)
            # h3 = (h2 + (r−1) × h″_int) / r
            # T₇ = ti + pincement  (le liquide sort de l'échangeur à ti + Δt_pincement)
            t7 = t_int + dt_pincement
            h7 = PropsSI('H', 'T', t7 + 273.15, 'P', p_k, fluide)
            # Bilan échangeur : ṁ_BP×(h5−h7) = ṁ_inj×(h″_int−h6) avec h6=h5
            # → r = 1 + (h5−h7) / (h″_int − h5)
            _dh_int  = h_vap_int - h_liq_int  # utilisé pour x6 plus bas
            _denom_r = h_vap_int - h5
            if abs(_denom_r) < 10.0:
                st.error("h″_int ≈ h₅ : pi trop proche de pk")
                return None
            r = 1.0 + (h5 - h7) / _denom_r
            if r <= 1.0:
                st.error(f"r = {r:.3f} ≤ 1 — ΔT_HX trop faible ou pi inadaptée")
                return None
            h3 = (h2 + (r - 1.0) * h_vap_int) / r
            s3 = calculer_propriete(fluide, 'S', H=h3, P=p_i)
            t3_r = calculer_propriete(fluide, 'T', H=h3, P=p_i)
            t3 = (t3_r - 273.15) if t3_r else t_int
            if h2 <= h3:
                st.error(f"h₂ ({h2/1000:.2f} kJ/kg) ≤ h₃ ({h3/1000:.2f} kJ/kg) — BP non surchauffé vs HP aspiration. Réduire pi ou augmenter ΔT_HX.")
                return None
            # Point 6 : liquide h5 expansé à pi (injection vers échangeur)
            h6 = h5
            x6 = (h5 - h_liq_int) / _dh_int if _dh_int > 0 else 0
            # Point 8 : h7 → p0 (détente BP isenthalpique)
            h8 = h7
            x8 = (h8 - h0_liq) / (h0_vap - h0_liq) if (h0_vap - h0_liq) > 0 else 0
            # Point 9 : sortie évap BP (surchauffe utile)
            t9   = to + surchauffe_evap_bp
            h9   = PropsSI('H', 'T', t9 + 273.15, 'P', p0, fluide)
            s9   = PropsSI('S', 'T', t9 + 273.15, 'P', p0, fluide)
            # Point 10 : sortie échangeur côté injection — vapeur saturée à pi
            h10_ip  = h_vap_int
            t10_ip  = t_int
            s10_ip  = s_vap_int
            bilan_str = f"T₇={t7:.1f}°C | h₇={h7/1000:.2f} kJ/kg | r = 1+(h₅−h₇)/(h″−h₅) = 1+({h5/1000:.2f}−{h7/1000:.2f})/({h_vap_int/1000:.2f}−{h5/1000:.2f}) = {r:.4f} | h₃={h3/1000:.2f} kJ/kg"

        else:  # Sous-refroidisseur (EVI)
            # Dérivation β = ṁ_bypass/ṁ_BP = (h5 - h5_sub) / (h_vap_int - h5)
            # h5_sub = liquide sous-refroidi après échangeur (sortie condenseur - sr_cond - dt_sub_hx)
            t5_sub = t5 - dt_sub_hx
            h5_sub = PropsSI('H', 'T', t5_sub + 273.15, 'P', p_k, fluide)
            denom_hx = h_vap_int - h5
            if abs(denom_hx) < 10.0:
                st.error("h_vap_int ≈ h5 : pi trop proche de pk")
                return None
            beta = (h5 - h5_sub) / denom_hx
            if beta <= 0:
                st.error(f"β = {beta:.4f} ≤ 0 — sous-refroidissement EVI incohérent (réduire ΔT_HX ou augmenter pi)")
                return None
            r = 1.0 + beta
            # HP suction : mélange BP discharge + bypass vapeur à pi
            h3 = (h2 + beta * h_vap_int) / (1.0 + beta)
            s3_r = calculer_propriete(fluide, 'S', H=h3, P=p_i)
            s3   = s3_r if s3_r else s_vap_int
            t3_r = calculer_propriete(fluide, 'T', H=h3, P=p_i)
            t3   = (t3_r - 273.15) if t3_r else t_int + 10
            # Point 6 : bypass h5 → pi (flash)
            h6 = h5
            x6 = (h5 - h_liq_int) / (h_vap_int - h_liq_int) if (h_vap_int - h_liq_int) > 0 else 0
            h7 = h_liq_int  # liq sat pi
            # Point 8 : h5_sub → p0 (liquide sous-refroidi → évaporateur)
            h8 = h5_sub
            x8 = (h8 - h0_liq) / (h0_vap - h0_liq) if (h0_vap - h0_liq) > 0 else 0
            # Overwrite h5 displayed as h5_sub for evaporator inlet
            t5_display = t5_sub
            bilan_str = f"β = (h₅ − h₅ₛᵤᵦ) / (h₃ − h₅) = ({h5/1000:.2f} − {h5_sub/1000:.2f}) / ({h_vap_int/1000:.2f} − {h5/1000:.2f}) = {beta:.4f}  →  r = 1+β = {r:.4f}"

        # ── POINT 4 : refoulement HP ─────────────────────────────────────────
        tc_k_sat = PropsSI('T', 'P', p_k, 'Q', 0, fluide)
        h4is = _compression_isentropique(fluide, s3, p_k, tc_k_sat, 'HP')
        t4is_r = calculer_propriete(fluide, 'T', H=h4is, P=p_k)
        t4is   = (t4is_r - 273.15) if t4is_r else tc + 30
        h4     = h3 + (h4is - h3) / eta_is_hp
        t4_r   = calculer_propriete(fluide, 'T', H=h4, P=p_k)
        t4     = (t4_r - 273.15) if t4_r else tc + 60
        s4     = calculer_propriete(fluide, 'S', H=h4, P=p_k)

        # ── DÉBITS MASSIQUES ─────────────────────────────────────────────────
        q_evap_specific = h1 - h8
        if q_evap_specific <= 0:
            st.error("Effet frigorifique négatif ou nul — vérifiez les paramètres")
            return None

        if type_entree == 'Puissance frigorifique [kW]':
            m_bp = valeur_entree * 1000 / q_evap_specific
        else:
            m_bp = (valeur_entree / 3600 * eta_vol_bp) / v1

        # Évaporateur MP (injection totale uniquement)
        if mode == 'Injection totale' and q_evap_mp > 0:
            _dh_int = h_vap_int - h_liq_int
            m_mp = q_evap_mp * 1000 / _dh_int
            # Bilan bouteille : ṁ_HP = [ṁ_BP×(h₂−h′) + ṁ_MP×(h″−h′)] / (h″−h₅)
            m_hp = (m_bp * (h2 - h_liq_int) + m_mp * _dh_int) / (h_vap_int - h5)
        else:
            # Cas standard : r = (h₂ − h′) / (h″ − h₅)
            r_std = (h2 - h_liq_int) / (h_vap_int - h5)
            if mode == 'Injection totale' and r_std <= 1.0:
                st.error(f"r = {r_std:.3f} ≤ 1 — conditions incompatibles")
                return None
            m_hp = r_std * m_bp if mode == 'Injection totale' else r * m_bp
            # Injection partielle : ṁ_inj = ṁ_HP − ṁ_BP
            m_mp = (m_hp - m_bp) if mode == 'Injection partielle' else 0.0

        r = m_hp / m_bp  # ratio affiché

        # ── PUISSANCES ───────────────────────────────────────────────────────
        w_bp    = m_bp * (h2 - h1) / 1000
        w_hp    = m_hp * (h4 - h3) / 1000
        # Pompe : calcul automatique à partir des données de dimensionnement
        if has_pump:
            # Masse volumique liquide saturé à pi (pompe côté MP)
            pump_rho     = PropsSI('D', 'P', p_i, 'Q', 0, fluide)
            qm_pump      = pump_n * m_mp if m_mp > 0 else pump_n * m_bp  # kg/s
            qv_pump_m3s  = qm_pump / pump_rho                     # m³/s
            hmt_pump     = pump_dp * 1e5 / (pump_rho * 9.81)     # m
            npsh_ok      = pump_height >= 1.5
            w_pump       = (qv_pump_m3s * pump_dp * 1e5) / (pump_eta * 1000)  # kW
            st.session_state.bi_pump_power = w_pump
            # Point 10 : sortie pompe (liquide à pi + pump_dp)
            dh_pump      = pump_dp * 1e5 / pump_rho               # J/kg
            h10          = h_liq_int + dh_pump
            p10_bar      = p_int_bar + pump_dp
            t10_r        = calculer_propriete(fluide, 'T', H=h10, P=p10_bar * 1e5)
            t10          = (t10_r - 273.15) if t10_r else t_int
            # Point 11 : sortie évap MP — mélange diphasique, titre = 1/n
            x11          = 1.0 / pump_n
            h11          = h_liq_int + x11 * (h_vap_int - h_liq_int)
            t11          = t_int
            p11_bar      = p_int_bar
        else:
            pump_rho = 0.0
            qm_pump = 0.0; qv_pump_m3s = 0.0; hmt_pump = 0.0
            npsh_ok = True; w_pump = 0.0
            h10 = h11 = None; t10 = t11 = None
            p10_bar = p11_bar = None
        w_total  = w_bp + w_hp + w_pump
        q_evap_bp = m_bp * q_evap_specific / 1000
        q_evap_mp_kw = m_mp * (h_vap_int - h_liq_int) / 1000 if m_mp > 0 else 0.0
        q_evap   = q_evap_bp + q_evap_mp_kw
        q_cond   = m_hp * (h4 - h5) / 1000

        v_bal_bp_m3h = (m_bp * v1       / eta_vol_bp) * 3600
        v_bal_hp_m3h = (m_hp * v_vap_int / eta_vol_hp) * 3600
        cop      = q_evap / w_total if w_total > 0 else 0
        tau_bp   = p_int_bar / (p0 / 1e5)
        tau_hp   = (p_k / 1e5) / p_int_bar

        # Point 8 température
        t8_r = calculer_propriete(fluide, 'T', H=h8, P=p0)
        t8   = (t8_r - 273.15) if t8_r else to

        return {
            'mode': mode,
            'points': {
                '1':   {'T': t1,    'P': p0/1e5,    'H': h1/1000,        'S': s1/1000 if s1 else None, 'V': v1,        'X': None},
                '2is': {'T': t2is,  'P': p_int_bar, 'H': h2is/1000,      'S': None,                    'V': None,      'X': None},
                '2':   {'T': t2,    'P': p_int_bar, 'H': h2/1000,        'S': s2/1000 if s2 else None, 'V': None,      'X': None},
                '3':   {'T': t3,    'P': p_int_bar, 'H': h3/1000,        'S': s3/1000 if s3 else None, 'V': v_vap_int if mode == 'Injection totale' else None, 'X': None},
                '4is': {'T': t4is,  'P': p_k/1e5,   'H': h4is/1000,      'S': None,                    'V': None,      'X': None},
                '4':   {'T': t4,    'P': p_k/1e5,   'H': h4/1000,        'S': s4/1000 if s4 else None, 'V': None,      'X': None},
                '5':   {'T': t5,    'P': p_k/1e5,   'H': h5/1000,        'S': None,                    'V': None,      'X': None},
                '6':   {'T': t_int, 'P': p_int_bar, 'H': h6/1000,        'S': None,                    'V': None,      'X': x6*100},
                '7':   {'T': t7 if mode == 'Injection partielle' else t_int,
                        'P': p_k/1e5 if mode == 'Injection partielle' else p_int_bar,
                        'H': h7/1000, 'S': None, 'V': None,
                        'X': None if mode == 'Injection partielle' else 0.0},
                '8':   {'T': t8,    'P': p0/1e5,    'H': h8/1000,        'S': None,                    'V': None,      'X': x8*100},
                **({'10': {'T': t10,  'P': p10_bar, 'H': h10/1000, 'S': None, 'V': None, 'X': None},
                    '11': {'T': t11,  'P': p11_bar, 'H': h11/1000, 'S': None, 'V': None, 'X': x11 * 100}}
                   if has_pump and m_mp > 0 and h10 is not None
                   and mode_original != 'Injection totale avec bouteille BP' else {}),
                **({'9':  {'T': t9,     'P': p0/1e5,    'H': h9/1000,    'S': s9/1000 if s9 else None,    'V': None, 'X': None},
                    '10': {'T': t10_ip, 'P': p_int_bar, 'H': h10_ip/1000,'S': s10_ip/1000 if s10_ip else None, 'V': None, 'X': 100.0}}
                   if mode_original == 'Injection partielle' else {}),
            },
            'intermediate': {
                't_int': t_int, 'p_int': p_int_bar,
                'h_liq': h_liq_int / 1000, 'h_vap': h_vap_int / 1000,
            },
            'performance': {
                'm_bp': m_bp, 'm_mp': m_mp, 'm_hp': m_hp, 'r': r,
                'q_evap': q_evap, 'q_evap_bp': q_evap_bp, 'q_evap_mp': q_evap_mp_kw, 'q_cond': q_cond,
                'w_bp': w_bp, 'w_hp': w_hp, 'w_pump': w_pump, 'w_total': w_total,
                'v_bal_bp': v_bal_bp_m3h, 'v_bal_hp': v_bal_hp_m3h,
                'cop': cop, 'tau_bp': tau_bp, 'tau_hp': tau_hp, 'x6': x6,
                'has_pump': has_pump,
                'pump_n': pump_n, 'pump_dp': pump_dp, 'pump_rho': pump_rho,
                'pump_eta': pump_eta, 'pump_height': pump_height,
                'qm_pump': qm_pump, 'qv_pump_m3h': qv_pump_m3s * 3600,
                'hmt_pump': hmt_pump, 'npsh_ok': npsh_ok,
            },
            'bilan_str': bilan_str,
            'fluide_affichage': fluide_affichage,
            'mode_original': mode_original,
        }

    except Exception as e:
        st.error(f"Erreur lors du calcul bi-étagé: {str(e)}")
        return None


# Initialisation de session_state
if 'fluide' not in st.session_state:
    st.session_state.fluide = FLUIDES[0]
if 'resultats' not in st.session_state:
    st.session_state.resultats = None
if 'calculer' not in st.session_state:
    st.session_state.calculer = False

# Réinitialisation des paramètres si demandé (avant création des widgets)
if st.session_state.get('reset_params', False):
    # Supprimer les clés pour permettre la réinitialisation
    keys_to_reset = ['to_evaporation', 'po_evaporation', 'tc_condensation', 'pk_condensation',
                     'echauffement_sup', 'refroidissement_sup', 'valeur_metrique']
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    # Réinitialiser aux valeurs par défaut
    st.session_state.rendement_vol = 0.85
    st.session_state.rendement_isen = 0.76
    st.session_state.surchauffe_utile = 5.0
    st.session_state.sous_refroid_cond = 5.0
    st.session_state.resultats = None
    st.session_state.reset_params = False

if 'rendement_vol' not in st.session_state:
    st.session_state.rendement_vol = 0.85
if 'rendement_isen' not in st.session_state:
    st.session_state.rendement_isen = 0.76
if 'surchauffe_utile' not in st.session_state:
    st.session_state.surchauffe_utile = 5.0
if 'sous_refroid_cond' not in st.session_state:
    st.session_state.sous_refroid_cond = 5.0
if 'to_evaporation' not in st.session_state:
    st.session_state.to_evaporation = None
if 'po_evaporation' not in st.session_state:
    st.session_state.po_evaporation = None
if 'tc_condensation' not in st.session_state:
    st.session_state.tc_condensation = None
if 'pk_condensation' not in st.session_state:
    st.session_state.pk_condensation = None
if 'show_diagram' not in st.session_state:
    st.session_state.show_diagram = False

# Session state pour l'onglet Bi-étagé
if 'bi_fluide' not in st.session_state:
    st.session_state.bi_fluide = FLUIDES[0]
if 'bi_mode' not in st.session_state:
    st.session_state.bi_mode = 'Injection totale'
if 'bi_pi_mode' not in st.session_state:
    st.session_state.bi_pi_mode = 'Auto (√(p₀×pₖ))'
if 'bi_surchauffe' not in st.session_state:
    st.session_state.bi_surchauffe = 5.0
if 'bi_sous_refroid' not in st.session_state:
    st.session_state.bi_sous_refroid = 5.0
if 'bi_eta_vol_bp' not in st.session_state:
    st.session_state.bi_eta_vol_bp = 0.78
if 'bi_eta_is_bp' not in st.session_state:
    st.session_state.bi_eta_is_bp = 0.75
if 'bi_eta_vol_hp' not in st.session_state:
    st.session_state.bi_eta_vol_hp = 0.78
if 'bi_eta_is_hp' not in st.session_state:
    st.session_state.bi_eta_is_hp = 0.75
if 'bi_type_entree' not in st.session_state:
    st.session_state.bi_type_entree = 'Puissance frigorifique [kW]'
if 'bi_valeur_entree' not in st.session_state:
    st.session_state.bi_valeur_entree = 0.0
if 'bi_resultats' not in st.session_state:
    st.session_state.bi_resultats = None
if 'bi_has_pump' not in st.session_state:
    st.session_state.bi_has_pump = False
if 'bi_pump_power' not in st.session_state:
    st.session_state.bi_pump_power = 0.0
if 'bi_pump_n' not in st.session_state:
    st.session_state.bi_pump_n = 3.0
if 'bi_pump_dp' not in st.session_state:
    st.session_state.bi_pump_dp = 0.5
if 'bi_pump_eta' not in st.session_state:
    st.session_state.bi_pump_eta = 0.60
if 'bi_pump_height' not in st.session_state:
    st.session_state.bi_pump_height = 2.0
if 'bi_dt_sub_hx' not in st.session_state:
    st.session_state.bi_dt_sub_hx = 5.0
if 'bi_dt_pincement' not in st.session_state:
    st.session_state.bi_dt_pincement = 5.0
if 'bi_surchauffe_evap_bp' not in st.session_state:
    st.session_state.bi_surchauffe_evap_bp = 5.0
if 'bi_q_evap_mp' not in st.session_state:
    st.session_state.bi_q_evap_mp = 0.0

# En-tête
st.markdown("""
    <div style="text-align: center; padding: 10px; border-bottom: 1px solid #e2e8f0; margin-bottom: 10px;">
        <h1 style="color: #2563eb; margin: 0;">❄️ Calculateur de Cycle Frigorifique</h1>
    </div>
""", unsafe_allow_html=True)

# ── Bannière publicitaire sous l'en-tête ─────────────────────────────────────
col_ad_center = st.columns([1, 3, 1])[1]
with col_ad_center:
    afficher_pub_adsense("horizontal")


# Mise à jour automatique des pressions/températures après validation
# Cette logique s'exécute après que l'utilisateur ait validé une valeur avec Entrée

# Calculer si demandé (avant l'affichage des onglets)
if st.session_state.get('calculer', False):
    resultats = calculer_cycle()
    if resultats:
        st.session_state.resultats = resultats
        st.success("✅ Calcul réussi!")
    else:
        st.error("❌ Erreur lors du calcul. Vérifiez vos paramètres.")
    st.session_state.calculer = False

# Style pour les boutons radio en mode onglets
st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:has(div[data-testid="stRadio"]) {
        background: transparent;
    }
    div[data-testid="stRadio"] > div {
        display: flex;
        gap: 0;
    }
    div[data-testid="stRadio"] label {
        background: #e2e8f0;
        padding: 10px 20px;
        border: 1px solid #cbd5e1;
        cursor: pointer;
        font-weight: 500;
    }
    div[data-testid="stRadio"] label:first-of-type {
        border-radius: 8px 0 0 8px;
    }
    div[data-testid="stRadio"] label:last-of-type {
        border-radius: 0 8px 8px 0;
    }
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: #2563eb;
        color: white;
        border-color: #2563eb;
    }
    </style>
""", unsafe_allow_html=True)

# ── PAGE D'ACCUEIL ────────────────────────────────────────────────────────────
if 'page' not in st.session_state:
    st.session_state.page = 'accueil'

if st.session_state.page == 'accueil':
    st.markdown("""
        <style>
        .accueil-hero {
            background: linear-gradient(135deg, #0f4c75 0%, #1b6ca8 60%, #2563eb 100%);
            padding: 40px 30px; border-radius: 16px; margin-bottom: 30px; text-align: center;
        }
        .accueil-card {
            background: white; border-radius: 12px; padding: 24px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 20px;
            border-left: 5px solid #2563eb;
        }
        .accueil-formula {
            background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px;
            padding: 12px 18px; font-family: monospace; font-size: 15px;
            margin: 8px 0; color: #0c4a6e;
        }
        .accueil-badge {
            display: inline-block; padding: 4px 12px; border-radius: 20px;
            font-size: 12px; font-weight: bold; margin: 4px;
        }
        </style>
    """, unsafe_allow_html=True)

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown("""
        <div class="accueil-hero">
            <h1 style="color:white; font-size:2.4em; margin:0 0 10px 0;">❄️ CalcFlu</h1>
            <p style="color:#bfdbfe; font-size:1.2em; margin:0 0 16px 0;">
                Calculateur de cycles frigorifiques pour ingénieurs HVAC
            </p>
            <p style="color:#93c5fd; font-size:0.95em;">
                Basé sur <strong style="color:white;">CoolProp</strong> — base de données thermodynamiques de référence (NIST/REFPROP)
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ── PRÉSENTATION ──────────────────────────────────────────────────────────
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("""
            <div class="accueil-card" style="border-color:#2563eb;">
                <h3 style="color:#1e40af; margin-top:0;">🎯 À qui s'adresse CalcFlu ?</h3>
                <p>CalcFlu est conçu pour les <strong>ingénieurs et techniciens du génie climatique et frigorifique</strong> qui ont besoin de :</p>
                <ul>
                    <li>Dimensionner des installations frigorifiques</li>
                    <li>Calculer des cycles thermodynamiques rigoureux</li>
                    <li>Comparer différentes architectures de cycles</li>
                    <li>Sélectionner un compresseur à partir des volumes balayés</li>
                    <li>Évaluer l'impact du choix du fluide frigorigène</li>
                </ul>
                <p>L'outil est adapté aux <strong>bureaux d'études</strong>, enseignants, étudiants en BTS/IUT/écoles d'ingénieurs, et techniciens terrain.</p>
            </div>
        """, unsafe_allow_html=True)
    with col_p2:
        st.markdown("""
            <div class="accueil-card" style="border-color:#7c3aed;">
                <h3 style="color:#5b21b6; margin-top:0;">⚙️ Possibilités de calcul</h3>
                <ul>
                    <li>✅ <strong>24 fluides frigorigènes</strong> : R134a, R410A, R32, R290, R744 (CO₂), R1234yf, R404A…</li>
                    <li>✅ Cycles <strong>mono-étagés</strong> avec surchauffe et sous-refroidissement</li>
                    <li>✅ Cycles <strong>bi-étagés — injection totale</strong> avec bouteille intermédiaire</li>
                    <li>✅ Cycles <strong>bi-étagés — injection partielle</strong> avec échangeur à plaques</li>
                    <li>✅ Calcul des <strong>volumes balayés</strong> BP et HP</li>
                    <li>✅ Calcul des <strong>débits massiques</strong> et puissances</li>
                    <li>✅ Dimensionnement de la <strong>pompe de recirculation</strong></li>
                    <li>✅ Tracé du <strong>diagramme P-h</strong></li>
                    <li>✅ Export <strong>PDF</strong> du bilan complet</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── CYCLE MONO-ÉTAGÉ ──────────────────────────────────────────────────────
    st.markdown("## 🔵 Cycle mono-étagé")
    col_m1, col_m2 = st.columns([1, 1])
    with col_m1:
        st.markdown("""
            <div class="accueil-card" style="border-color:#1976d2;">
                <h4 style="color:#1565c0; margin-top:0;">Principe</h4>
                <p>Le cycle de réfrigération à compression de vapeur comprend 4 transformations :</p>
                <ol>
                    <li><strong>1→2</strong> Compression (compresseur) — adiabatique</li>
                    <li><strong>2→3</strong> Condensation (condenseur) — rejet de chaleur</li>
                    <li><strong>3→4</strong> Détente (détendeur) — isenthalpique</li>
                    <li><strong>4→1</strong> Évaporation (évaporateur) — absorption de chaleur</li>
                </ol>
                <h4 style="color:#1565c0;">Paramètres d'entrée</h4>
                <ul>
                    <li>Température / pression d'évaporation t₀ ou p₀</li>
                    <li>Température / pression de condensation tₖ ou pₖ</li>
                    <li>Surchauffe à l'aspiration [K]</li>
                    <li>Sous-refroidissement au condenseur [K]</li>
                    <li>Rendements volumétrique et isentropique [-]</li>
                    <li>Puissance frigorifique [kW] ou volume balayé [m³/h]</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown("""
            <div class="accueil-card" style="border-color:#1976d2;">
                <h4 style="color:#1565c0; margin-top:0;">Formules clés</h4>
                <div class="accueil-formula">h₁ = h(T₀ + ΔT_surch, p₀)  — aspiration</div>
                <div class="accueil-formula">h₂ = h₁ + (h₂ₛ − h₁) / ηᵢₛ  — refoulement réel</div>
                <div class="accueil-formula">q₀ = h₁ − h₄  — effet frigorifique [kJ/kg]</div>
                <div class="accueil-formula">w = h₂ − h₁  — travail compresseur [kJ/kg]</div>
                <div class="accueil-formula">COP = q₀ / w = Q₀ / W_comp</div>
                <div class="accueil-formula">ṁ = Q₀ / q₀  [kg/s]</div>
                <div class="accueil-formula">Vb = ṁ × v₁ / ηvol  [m³/s]</div>
                <div class="accueil-formula">ηvol = 1 − c × (τ − 1)  avec τ = pₖ/p₀</div>
                <p style="font-size:11px; color:#666; margin-top:10px;">
                    v₁ = volume massique à l'aspiration [m³/kg] | c = taux de volumes morts (≈ 0.04)
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── CYCLE BI-ÉTAGÉ ────────────────────────────────────────────────────────
    st.markdown("## 🟣 Cycle bi-étagé")
    st.markdown("""
        <div class="accueil-card" style="border-color:#7b1fa2;">
            <h4 style="color:#6a1b9a; margin-top:0;">Pourquoi un cycle bi-étagé ?</h4>
            <p>Lorsque le taux de compression <strong>τ = pₖ/p₀ dépasse 6 à 8</strong>, le cycle mono-étagé devient inefficace
            (forte surchauffe au refoulement, faible rendement volumétrique). Le cycle bi-étagé introduit une
            <strong>pression intermédiaire pi</strong> pour diviser la compression en deux étages, améliorant le COP et la fiabilité.</p>
            <p>La pression intermédiaire optimale minimisant le travail total est :</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="accueil-formula" style="text-align:center; font-size:18px;">pi = √(p₀ × pₖ)  → taux de compression égaux : τ_BP = τ_HP = √τ_total</div>', unsafe_allow_html=True)

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("""
            <div class="accueil-card" style="border-color:#0f4c75;">
                <h4 style="color:#0f4c75; margin-top:0;">🔀 Injection totale</h4>
                <p>Tout le liquide du condenseur passe par la <strong>bouteille intermédiaire à pi</strong>.
                La vapeur saturée alimente le compresseur HP, le liquide saturé est détendu vers l'évaporateur BP.</p>
                <div class="accueil-formula">r = (h₂ − h₇) / (h₃ − h₅)</div>
                <div class="accueil-formula">ṁ_HP = r × ṁ_BP</div>
                <p style="font-size:12px; color:#555;">Variante disponible : injection totale avec <strong>bouteille BP</strong>
                (évaporateur noyé avec pompe de recirculation côté basse pression)</p>
            </div>
        """, unsafe_allow_html=True)
    with col_b2:
        st.markdown("""
            <div class="accueil-card" style="border-color:#00695c;">
                <h4 style="color:#00695c; margin-top:0;">💉 Injection partielle</h4>
                <p>Une fraction du liquide est dérivée, détendue à pi, et <strong>injectée via un échangeur à plaques</strong>
                pour sous-refroidir le liquide principal et désurchauffer le refoulement BP.</p>
                <div class="accueil-formula">T₇ = ti + Δt_pincement</div>
                <div class="accueil-formula">r = 1 + (h₅ − h₇) / (h″_pi − h₅)</div>
                <div class="accueil-formula">h₃ = (ṁ_BP×h₂ + ṁ_inj×h₁₀) / ṁ_HP</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── GUIDE D'UTILISATION ───────────────────────────────────────────────────
    st.markdown("## 📋 Guide d'utilisation pas à pas")
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        st.markdown("""
            <div class="accueil-card" style="border-color:#f59e0b;">
                <h4 style="color:#d97706; margin-top:0;">① Saisir les conditions</h4>
                <ul>
                    <li>Choisir le <strong>fluide frigorigène</strong></li>
                    <li>Entrer la <strong>température ou pression</strong> d'évaporation — l'autre est calculée automatiquement</li>
                    <li>Entrer la <strong>température ou pression</strong> de condensation</li>
                    <li>Renseigner surchauffe et sous-refroidissement</li>
                    <li>Vérifier les rendements (calculés automatiquement à partir de τ)</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    with col_g2:
        st.markdown("""
            <div class="accueil-card" style="border-color:#10b981;">
                <h4 style="color:#059669; margin-top:0;">② Choisir la donnée de dimensionnement</h4>
                <ul>
                    <li><strong>Puissance frigorifique Q₀ [kW]</strong> → CalcFlu calcule les débits et volumes balayés</li>
                    <li><strong>Volume balayé [m³/h]</strong> → CalcFlu calcule la puissance et les débits</li>
                </ul>
                <p>Pour le bi-étagé, vous pouvez aussi saisir la <strong>puissance de l'étage MP</strong> (évaporateur intermédiaire).</p>
            </div>
        """, unsafe_allow_html=True)
    with col_g3:
        st.markdown("""
            <div class="accueil-card" style="border-color:#ef4444;">
                <h4 style="color:#dc2626; margin-top:0;">③ Lire les résultats</h4>
                <ul>
                    <li><strong>Tuiles colorées</strong> : Q₀, Qₖ, W_comp, COP</li>
                    <li><strong>Volumes balayés</strong> BP et HP en m³/h</li>
                    <li><strong>Débits massiques</strong> ṁ BP et ṁ HP en kg/h</li>
                    <li><strong>Tableau des points</strong> du cycle (T, P, h, s)</li>
                    <li><strong>Diagramme P-h</strong> interactif</li>
                    <li><strong>Export PDF</strong> du bilan complet</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── PUBLICITÉ ─────────────────────────────────────────────────────────────
    afficher_pub_adsense("horizontal")

    # ── UNITÉS ────────────────────────────────────────────────────────────────
    st.markdown("## 📐 Unités et conventions")
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.markdown("""
            | Grandeur | Unité affichée | Unité interne |
            |----------|---------------|---------------|
            | Pression | bar abs | Pa |
            | Température | °C | K |
            | Enthalpie | kJ/kg | J/kg |
            | Entropie | kJ/(kg·K) | J/(kg·K) |
            | Débit massique | kg/h | kg/s |
        """)
    with col_u2:
        st.markdown("""
            | Grandeur | Unité affichée | Unité interne |
            |----------|---------------|---------------|
            | Volume spécifique | m³/kg | m³/kg |
            | Volume balayé | m³/h | m³/s |
            | Puissance | kW | W |
            | COP | — | — |
            | Taux de compression | — | — |
        """)

    st.markdown("---")

    # ── BOUTON DÉMARRER ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("🚀 Accéder à l'application", type="primary",
                     use_container_width=True, key='btn_demarrer'):
            st.session_state.page = 'app'
            st.rerun()

    st.markdown("""
        <div style="text-align:center; color:#94a3b8; font-size:12px; margin-top:30px;">
            CalcFlu — Développé par Christian Lucas | Motorisé par CoolProp & Streamlit<br>
            Les calculs sont basés sur les propriétés thermodynamiques réelles des fluides (équations d'état NIST).
        </div>
    """, unsafe_allow_html=True)

    st.stop()

# Sélection d'onglet avec état persistant
if 'onglet_actif' not in st.session_state:
    st.session_state.onglet_actif = "Cycle mono-étagé"

_nav_options = ["Cycle mono-étagé", "Choix de compresseur", "Bi-étagé", "Calculateur"]
onglet_selectionne = st.radio(
    "Navigation",
    _nav_options,
    index=_nav_options.index(st.session_state.onglet_actif) if st.session_state.onglet_actif in _nav_options else 0,
    horizontal=True,
    key='nav_onglets',
    label_visibility="collapsed"
)
st.session_state.onglet_actif = onglet_selectionne

st.markdown("---")

if onglet_selectionne == "Cycle mono-étagé":
    # Grille 2x2
    col_schema, col_params = st.columns([1, 1])
    
    with col_schema:
        # SECTION 1 : Schéma (haut-gauche)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Schéma</div>', unsafe_allow_html=True)
        
        # Image du schéma
        try:
            image_path = resource_path("circuitFrigo.png")
            if os.path.exists(image_path):
                _res_mono = st.session_state.get('resultats')
                if _res_mono and _res_mono.get('performance'):
                    _fluide_mono = st.session_state.get('fluide', '')
                    image = superposer_schema_mono(image_path, _res_mono['performance'], _fluide_mono)
                else:
                    image = Image.open(image_path)
                target_width = int(image.width * 0.8)
                target_height = int(image.height * 0.8)
                image_resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                st.image(image_resized, use_container_width=False)
        except:
            pass
        
        # Labels du schéma - Conditions BP et HP
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        col_t0, col_tk = st.columns(2)
        with col_t0:
            t0_val = st.session_state.get('to_evaporation')
            p0_val = st.session_state.get('po_evaporation')
            t0_display = f"{t0_val:.2f}" if t0_val is not None else "---"
            p0_display = f"{p0_val:.2f}" if p0_val is not None else "---"
            st.markdown(f'''
                <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                            border: 2px solid #1976d2; border-radius: 8px; padding: 12px; margin: 5px 0;">
                    <div style="font-size: 12px; color: #1565c0; font-weight: bold; margin-bottom: 5px;">❄️ BASSE PRESSION</div>
                    <div style="font-size: 18px; color: #0d47a1; font-weight: bold;">t₀ = {t0_display} °C</div>
                    <div style="font-size: 18px; color: #0d47a1; font-weight: bold;">p₀ = {p0_display} bar</div>
                </div>
            ''', unsafe_allow_html=True)

        with col_tk:
            tk_val = st.session_state.get('tc_condensation')
            pk_val = st.session_state.get('pk_condensation')
            tk_display = f"{tk_val:.2f}" if tk_val is not None else "---"
            pk_display = f"{pk_val:.2f}" if pk_val is not None else "---"
            st.markdown(f'''
                <div style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
                            border: 2px solid #d32f2f; border-radius: 8px; padding: 12px; margin: 5px 0;">
                    <div style="font-size: 12px; color: #c62828; font-weight: bold; margin-bottom: 5px;">🔥 HAUTE PRESSION</div>
                    <div style="font-size: 18px; color: #b71c1c; font-weight: bold;">tₖ = {tk_display} °C</div>
                    <div style="font-size: 18px; color: #b71c1c; font-weight: bold;">pₖ = {pk_display} bar</div>
                </div>
            ''', unsafe_allow_html=True)

        # Totaux surchauffe et sous-refroidissement
        surch_val = st.session_state.get('surchauffe_utile', 5.0) or 0
        echauf_val = st.session_state.get('echauffement_sup', 0.0) or 0
        surch_tot = surch_val + echauf_val

        sous_ref_val = st.session_state.get('sous_refroid_cond', 5.0) or 0
        refroid_val = st.session_state.get('refroidissement_sup', 0.0) or 0
        sous_ref_tot = sous_ref_val + refroid_val

        col_sur, col_sous = st.columns(2)
        with col_sur:
            st.markdown(f'''
                <div style="background: #f5f5f5; border-left: 4px solid #1976d2;
                            padding: 10px; border-radius: 4px; margin: 8px 0;">
                    <div style="font-size: 13px; color: #333; font-weight: bold;">
                        🔼 Surchauffe totale: <span style="color: #1565c0; font-size: 16px;">{surch_tot:.1f} K</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

        with col_sous:
            st.markdown(f'''
                <div style="background: #f5f5f5; border-left: 4px solid #d32f2f;
                            padding: 10px; border-radius: 4px; margin: 8px 0;">
                    <div style="font-size: 13px; color: #333; font-weight: bold;">
                        🔽 Sous-refroid. total: <span style="color: #c62828; font-size: 16px;">{sous_ref_tot:.1f} K</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_params:
        # SECTION 2 : Cycle mono-étagé (haut-droite)

        # Callbacks pour mise à jour automatique T <-> P
        def on_to_change():
            """Callback quand la température d'évaporation change"""
            try:
                to_val = st.session_state.get('to_evaporation')
                if to_val is not None:
                    fluide = obtenir_fluide_coolprop(st.session_state.fluide)
                    temp_evap_k = to_val + 273.15
                    pression_evap_pa = None
                    for q in [1, 0.5, 0]:
                        try:
                            pression_evap_pa = PropsSI('P', 'T', temp_evap_k, 'Q', q, fluide)
                            if pression_evap_pa:
                                break
                        except:
                            continue
                    if pression_evap_pa:
                        st.session_state.po_evaporation = pression_evap_pa / 1e5
                        # Mettre à jour le rendement vol suggéré après avoir mis à jour po
                        pk_val = st.session_state.get('pk_condensation')
                        if pk_val and pk_val > 0:
                            po_val = pression_evap_pa / 1e5
                            taux_compression = pk_val / po_val
                            rendement_vol = 1 - (0.04 * taux_compression)
                            rendement_vol = max(0.3, min(0.98, rendement_vol))
                            st.session_state.rendement_vol = round(rendement_vol, 2)
            except:
                pass

        def calculer_rendement_vol_suggere():
            """Calcule le rendement volumétrique suggéré à partir du taux de compression"""
            try:
                po_val = st.session_state.get('po_evaporation')
                pk_val = st.session_state.get('pk_condensation')
                if po_val and pk_val and po_val > 0 and pk_val > 0:
                    taux_compression = pk_val / po_val
                    rendement_vol = 1 - (0.04 * taux_compression)
                    # Limiter entre 0.3 et 0.98
                    rendement_vol = max(0.3, min(0.98, rendement_vol))
                    st.session_state.rendement_vol = round(rendement_vol, 2)
            except:
                pass

        def on_po_change():
            """Callback quand la pression d'évaporation change"""
            try:
                po_val = st.session_state.get('po_evaporation')
                if po_val is not None and po_val > 0:
                    fluide = obtenir_fluide_coolprop(st.session_state.fluide)
                    pression_evap_pa = po_val * 1e5
                    temp_evap_k = None
                    for q in [1, 0.5, 0]:
                        try:
                            temp_evap_k = PropsSI('T', 'P', pression_evap_pa, 'Q', q, fluide)
                            if temp_evap_k:
                                break
                        except:
                            continue
                    if temp_evap_k:
                        st.session_state.to_evaporation = temp_evap_k - 273.15
                    # Mettre à jour le rendement vol suggéré
                    calculer_rendement_vol_suggere()
            except:
                pass

        def on_tc_change():
            """Callback quand la température de condensation change"""
            try:
                tc_val = st.session_state.get('tc_condensation')
                if tc_val is not None:
                    fluide = obtenir_fluide_coolprop(st.session_state.fluide)
                    temp_cond_k = tc_val + 273.15
                    pression_cond_pa = None
                    for q in [0, 0.5, 1]:
                        try:
                            pression_cond_pa = PropsSI('P', 'T', temp_cond_k, 'Q', q, fluide)
                            if pression_cond_pa:
                                break
                        except:
                            continue
                    if pression_cond_pa:
                        st.session_state.pk_condensation = pression_cond_pa / 1e5
                        # Mettre à jour le rendement vol suggéré
                        calculer_rendement_vol_suggere()
            except:
                pass

        def on_pk_change():
            """Callback quand la pression de condensation change"""
            try:
                pk_val = st.session_state.get('pk_condensation')
                if pk_val is not None and pk_val > 0:
                    fluide = obtenir_fluide_coolprop(st.session_state.fluide)
                    pression_cond_pa = pk_val * 1e5
                    temp_cond_k = None
                    for q in [0, 0.5, 1]:
                        try:
                            temp_cond_k = PropsSI('T', 'P', pression_cond_pa, 'Q', q, fluide)
                            if temp_cond_k:
                                break
                        except:
                            continue
                    if temp_cond_k:
                        st.session_state.tc_condensation = temp_cond_k - 273.15
                    # Mettre à jour le rendement vol suggéré
                    calculer_rendement_vol_suggere()
            except:
                pass

        # Sélection du fluide avec style
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 10px 15px; border-radius: 8px; margin-bottom: 15px;">
                <span style="color: white; font-weight: bold; font-size: 14px;">🧪 Fluide frigorigène</span>
            </div>
        """, unsafe_allow_html=True)

        fluide = st.selectbox(
            "Sélectionner le fluide",
            FLUIDES,
            index=FLUIDES.index(st.session_state.fluide) if st.session_state.fluide in FLUIDES else 0,
            key='fluide',
            label_visibility="collapsed"
        )

        # Deux colonnes pour Évaporation et Condensation
        col_evap, col_cond = st.columns(2)

        with col_evap:
            # Section Évaporation (Basse Pression) - Bleu
            st.markdown("""
                <div style="background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
                            padding: 8px 12px; border-radius: 8px; margin-bottom: 10px;">
                    <span style="color: white; font-weight: bold; font-size: 13px;">❄️ ÉVAPORATION (BP)</span>
                </div>
            """, unsafe_allow_html=True)

            st.number_input(
                "Température t₀ [°C]",
                value=st.session_state.get('to_evaporation'),
                key='to_evaporation',
                format="%.2f",
                on_change=on_to_change,
                help="Température de rosée (dew) pour les mélanges - point de saturation vapeur"
            )
            st.number_input(
                "Pression p₀ [bar abs]",
                value=st.session_state.get('po_evaporation'),
                key='po_evaporation',
                format="%.2f",
                on_change=on_po_change,
                help="Pression absolue à l'évaporateur"
            )
            st.number_input(
                "Surchauffe utile [K]",
                value=st.session_state.get('surchauffe_utile', 5.0),
                key='surchauffe_utile',
                min_value=0.0,
                max_value=30.0,
                step=1.0,
                format="%.0f",
                help="Surchauffe dans l'évaporateur (typique: 5-8K)"
            )
            st.number_input(
                "Surchauffe ligne asp. [K]",
                value=st.session_state.get('echauffement_sup', 0.0),
                key='echauffement_sup',
                min_value=0.0,
                max_value=20.0,
                step=1.0,
                format="%.0f",
                help="Échauffement supplémentaire dans la ligne d'aspiration"
            )

        with col_cond:
            # Section Condensation (Haute Pression) - Rouge
            st.markdown("""
                <div style="background: linear-gradient(135deg, #e53935 0%, #c62828 100%);
                            padding: 8px 12px; border-radius: 8px; margin-bottom: 10px;">
                    <span style="color: white; font-weight: bold; font-size: 13px;">🔥 CONDENSATION (HP)</span>
                </div>
            """, unsafe_allow_html=True)

            st.number_input(
                "Température tₖ [°C]",
                value=st.session_state.get('tc_condensation'),
                key='tc_condensation',
                format="%.2f",
                on_change=on_tc_change,
                help="Température de bulle (bubble) pour les mélanges - point de saturation liquide"
            )
            st.number_input(
                "Pression pₖ [bar abs]",
                value=st.session_state.get('pk_condensation'),
                key='pk_condensation',
                format="%.2f",
                on_change=on_pk_change,
                help="Pression absolue au condenseur"
            )
            st.number_input(
                "Sous-refroidissement [K]",
                value=st.session_state.get('sous_refroid_cond', 5.0),
                key='sous_refroid_cond',
                min_value=0.0,
                max_value=30.0,
                step=1.0,
                format="%.0f",
                help="Sous-refroidissement au condenseur (typique: 3-8K)"
            )
            st.number_input(
                "Refroid. ligne liq. [K]",
                value=st.session_state.get('refroidissement_sup', 0.0),
                key='refroidissement_sup',
                min_value=0.0,
                max_value=20.0,
                step=1.0,
                format="%.0f",
                help="Refroidissement supplémentaire dans la ligne liquide"
            )

        # Section Compresseur - Violet
        st.markdown("""
            <div style="background: linear-gradient(135deg, #7b1fa2 0%, #6a1b9a 100%);
                        padding: 8px 12px; border-radius: 8px; margin: 15px 0 10px 0;">
                <span style="color: white; font-weight: bold; font-size: 13px;">⚙️ COMPRESSEUR</span>
            </div>
        """, unsafe_allow_html=True)

        col_rend1, col_rend2 = st.columns(2)
        with col_rend1:
            st.number_input(
                "Rendement volumétrique [-]",
                value=st.session_state.get('rendement_vol', 0.85),
                key='rendement_vol',
                min_value=0.1,
                max_value=1.0,
                step=0.01,
                format="%.2f",
                help="Rendement volumétrique du compresseur (typique: 0.7-0.9)"
            )
        with col_rend2:
            st.number_input(
                "Rendement isentropique [-]",
                value=st.session_state.get('rendement_isen', 0.76),
                key='rendement_isen',
                min_value=0.1,
                max_value=1.0,
                step=0.01,
                format="%.2f",
                help="Rendement isentropique du compresseur (typique: 0.65-0.85)"
            )

        # Section Dimensionnement - Vert
        st.markdown("""
            <div style="background: linear-gradient(135deg, #43a047 0%, #2e7d32 100%);
                        padding: 8px 12px; border-radius: 8px; margin: 15px 0 10px 0;">
                <span style="color: white; font-weight: bold; font-size: 13px;">📐 DIMENSIONNEMENT</span>
            </div>
        """, unsafe_allow_html=True)

        col_type, col_val = st.columns([1, 1])
        with col_type:
            type_metrique = st.selectbox(
                "Donnée d'entrée",
                ['Puissance frigorifique utile', 'Volume balayé'],
                index=1 if st.session_state.get('type_metrique', 'Puissance frigorifique utile') == 'Volume balayé' else 0,
                key='type_metrique',
                help="Choisir le paramètre de dimensionnement"
            )

        with col_val:
            if type_metrique == 'Volume balayé':
                st.number_input(
                    "Volume balayé [m³/h]",
                    value=st.session_state.get('valeur_metrique', 0.0),
                    key='valeur_metrique',
                    min_value=0.0,
                    step=1.0,
                    format="%.1f",
                    help="Volume balayé théorique du compresseur en m³/h"
                )
            else:
                st.number_input(
                    "Puissance frigo [kW]",
                    value=st.session_state.get('valeur_metrique', 0.0),
                    key='valeur_metrique',
                    min_value=0.0,
                    step=0.1,
                    format="%.2f",
                    help="Puissance frigorifique utile souhaitée"
                )

        # Boutons et diagramme
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_diag = st.columns([1, 1, 2])

        with col_btn1:
            if st.button("🔄 CALCULER LE CYCLE", type="primary", use_container_width=True):
                st.session_state.calculer = True
                st.rerun()

        with col_btn2:
            if st.button("🗑️ Effacer", use_container_width=True):
                # Utiliser un flag pour réinitialiser au prochain rerun
                st.session_state.reset_params = True
                st.rerun()

        with col_diag:
            # Diagramme P-h en miniature
            try:
                diag_path = resource_path("diag.png")
                if os.path.exists(diag_path):
                    diag_image = Image.open(diag_path)
                    # Redimensionner en petite taille (200px de large)
                    target_width = 250
                    aspect_ratio = diag_image.height / diag_image.width
                    target_height = int(target_width * aspect_ratio)
                    diag_resized = diag_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    st.image(diag_resized, caption=f"📊 Diag. P-h - {st.session_state.fluide}")
            except:
                pass
    
    # Ligne du bas
    col_resultats, col_tableau = st.columns([1, 1])
    
    with col_resultats:
        # SECTION 3 : Résultats (bas-gauche)
        st.markdown("""
            <div style="background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
                        padding: 8px 12px; border-radius: 8px; margin-bottom: 10px;">
                <span style="color: white; font-weight: bold; font-size: 13px;">📊 RÉSULTATS DU CYCLE</span>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.resultats:
            resultats = st.session_state.resultats
            perf = resultats['performance']
            points = resultats['points']

            # Ligne 0 : Conditions BP et HP
            col_bp, col_hp = st.columns(2)
            with col_bp:
                t0_val = points['0']['T']
                p0_val = points['0']['P']
                surch_utile = st.session_state.get('surchauffe_utile', 0) or 0
                surch_ligne = st.session_state.get('echauffement_sup', 0) or 0
                surch_tot = surch_utile + surch_ligne
                st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                                border: 2px solid #1976d2; border-radius: 8px; padding: 10px; margin: 5px 0;">
                        <div style="font-size: 11px; color: #1565c0; font-weight: bold;">❄️ BASSE PRESSION</div>
                        <div style="font-size: 16px; color: #0d47a1; font-weight: bold;">t₀ = {t0_val:.2f} °C | p₀ = {p0_val:.2f} bar</div>
                        <div style="font-size: 12px; color: #1976d2;">Surchauffe totale: {surch_tot:.1f} K</div>
                    </div>
                ''', unsafe_allow_html=True)

            with col_hp:
                tk_val = points['3']['T']
                pk_val = points['3']['P']
                sous_ref = st.session_state.get('sous_refroid_cond', 0) or 0
                refroid_ligne = st.session_state.get('refroidissement_sup', 0) or 0
                sous_ref_tot = sous_ref + refroid_ligne
                st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
                                border: 2px solid #d32f2f; border-radius: 8px; padding: 10px; margin: 5px 0;">
                        <div style="font-size: 11px; color: #c62828; font-weight: bold;">🔥 HAUTE PRESSION</div>
                        <div style="font-size: 16px; color: #b71c1c; font-weight: bold;">tₖ = {tk_val:.2f} °C | pₖ = {pk_val:.2f} bar</div>
                        <div style="font-size: 12px; color: #c62828;">Sous-refroid. total: {sous_ref_tot:.1f} K</div>
                    </div>
                ''', unsafe_allow_html=True)

            # Ligne 1 : Puissances principales
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown(f'''
                    <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 10px; border-radius: 4px; margin: 5px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">❄️ Puissance frigorifique</div>
                        <div style="font-size: 20px; color: #2e7d32; font-weight: bold;">{perf['puissance_frigorifique']:.2f} kW</div>
                    </div>
                ''', unsafe_allow_html=True)

            with col_r2:
                st.markdown(f'''
                    <div style="background: #ffebee; border-left: 4px solid #f44336; padding: 10px; border-radius: 4px; margin: 5px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">🔥 Puissance calorifique</div>
                        <div style="font-size: 20px; color: #c62828; font-weight: bold;">{perf['puissance_condensation']:.2f} kW</div>
                    </div>
                ''', unsafe_allow_html=True)

            # Ligne 2 : Puissance compression et COP
            col_r3, col_r4 = st.columns(2)
            with col_r3:
                st.markdown(f'''
                    <div style="background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 10px; border-radius: 4px; margin: 5px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">⚡ Puissance compression</div>
                        <div style="font-size: 20px; color: #7b1fa2; font-weight: bold;">{perf['puissance_compression']:.2f} kW</div>
                    </div>
                ''', unsafe_allow_html=True)

            with col_r4:
                cop_color = "#4caf50" if perf['cop'] >= 3 else ("#ff9800" if perf['cop'] >= 2 else "#f44336")
                st.markdown(f'''
                    <div style="background: #fff8e1; border-left: 4px solid #ff9800; padding: 10px; border-radius: 4px; margin: 5px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">🎯 COP (Efficacité)</div>
                        <div style="font-size: 20px; color: {cop_color}; font-weight: bold;">{perf['cop']:.2f}</div>
                    </div>
                ''', unsafe_allow_html=True)

            # Ligne 3 : Volume balayé et débit massique
            col_r5, col_r6 = st.columns(2)
            with col_r5:
                vol_bal = perf.get('volume_balaye', 0.0) * 3600  # m³/s -> m³/h
                st.markdown(f'''
                    <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 10px; border-radius: 4px; margin: 5px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">📦 Volume balayé</div>
                        <div style="font-size: 18px; color: #1565c0; font-weight: bold;">{vol_bal:.2f} m³/h</div>
                    </div>
                ''', unsafe_allow_html=True)

            with col_r6:
                st.markdown(f'''
                    <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 10px; border-radius: 4px; margin: 5px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">💧 Débit massique</div>
                        <div style="font-size: 18px; color: #1565c0; font-weight: bold;">{perf['debit_massique']:.4f} kg/s</div>
                    </div>
                ''', unsafe_allow_html=True)

            # Ligne 4 : Taux de compression et température refoulement
            col_r7, col_r8 = st.columns(2)
            taux_comp = resultats['points']['2']['P'] / resultats['points']['0']['P'] if resultats['points']['0']['P'] > 0 else 0
            t_refoulement = resultats['points']['2']['T']

            with col_r7:
                taux_color = "#4caf50" if taux_comp <= 8 else ("#ff9800" if taux_comp <= 12 else "#f44336")
                st.markdown(f'''
                    <div style="background: #fafafa; border-left: 4px solid #607d8b; padding: 10px; border-radius: 4px; margin: 5px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">📈 Taux compression (HP/BP)</div>
                        <div style="font-size: 18px; color: {taux_color}; font-weight: bold;">{taux_comp:.2f}</div>
                    </div>
                ''', unsafe_allow_html=True)

            with col_r8:
                t_color = "#4caf50" if t_refoulement <= 100 else ("#ff9800" if t_refoulement <= 120 else "#f44336")
                st.markdown(f'''
                    <div style="background: #fafafa; border-left: 4px solid #607d8b; padding: 10px; border-radius: 4px; margin: 5px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">🌡️ Temp. refoulement</div>
                        <div style="font-size: 18px; color: {t_color}; font-weight: bold;">{t_refoulement:.1f} °C</div>
                    </div>
                ''', unsafe_allow_html=True)

        else:
            st.info("👆 Renseignez les paramètres et cliquez sur 'CALCULER LE CYCLE'")
    
    with col_tableau:
        # SECTION 4 : Tableau (bas-droite)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Résultats cycle</div>', unsafe_allow_html=True)
        
        if st.session_state.resultats:
            resultats = st.session_state.resultats
            points = resultats['points']
            
            # Tableau
            tableau_data = []
            for point_name in ['0', '1', '2is', '2', '3', "3'", '4', '5']:
                point = points[point_name]
                v_x = f"{point['V']:.4f}" if point['V'] is not None else (f"X={point['X']:.2f}%" if point['X'] is not None else "---")
                tableau_data.append({
                    'Point': point_name,
                    'pression abs [bar]': f"{point['P']:.2f}" if point['P'] is not None else "---",
                    'temp [°C]': f"{point['T']:.2f}" if point['T'] is not None else "---",
                    'enthalpie [kJ/kg]': f"{point['H']:.2f}" if point['H'] is not None else "---",
                    'entropie [kJ/(kg·K)]': f"{point['S']:.2f}" if point['S'] is not None else "---",
                    'Vol massique / X [m³/kg / %]': v_x
                })
            
            st.dataframe(tableau_data, use_container_width=True, hide_index=True)

            # Bouton export PDF
            st.markdown("---")
            if st.button("📄 Exporter en PDF", key='btn_mono_pdf'):
                try:
                    _fluide_mono = st.session_state.get('fluide', '')
                    _img_path = resource_path("circuitFrigo.png")
                    _schema_pil = superposer_schema_mono(_img_path, resultats['performance'], _fluide_mono) if os.path.exists(_img_path) else None
                    _pdf_buf = generer_pdf_mono(resultats, _fluide_mono, _schema_pil)
                    st.download_button(
                        label="⬇️ Télécharger le PDF",
                        data=_pdf_buf,
                        file_name=f"calcflu_mono_{_fluide_mono}.pdf",
                        mime="application/pdf",
                        key='dl_mono_pdf'
                    )
                except Exception as _e:
                    st.error(f"Erreur génération PDF : {_e}")
        else:
            st.info("Cliquez sur 'Calculer' pour afficher les résultats")

        st.markdown('</div>', unsafe_allow_html=True)

elif onglet_selectionne == "Choix de compresseur":
    st.header("Choix de compresseur")

    # Initialiser les variables de session pour cet onglet
    if 'h1_catalogue' not in st.session_state:
        st.session_state.h1_catalogue = None
    if 'h4_catalogue' not in st.session_state:
        st.session_state.h4_catalogue = None
    if 'v1_catalogue' not in st.session_state:
        st.session_state.v1_catalogue = None
    if 'kcat' not in st.session_state:
        st.session_state.kcat = None
    if 'puissance_catalogue' not in st.session_state:
        st.session_state.puissance_catalogue = None

    # Ligne 1 : Valeurs cycle et Conditions catalogue côte à côte
    col_valeurs, col_catalogue = st.columns(2)

    with col_valeurs:
        # SECTION 1 : Valeurs pour le choix du compresseur (issues du cycle calculé)
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
                        padding: 8px 12px; border-radius: 8px; margin-bottom: 10px;">
                <span style="color: white; font-weight: bold; font-size: 13px;">📊 VALEURS DU CYCLE CALCULÉ</span>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.resultats is None:
            st.warning("⚠️ Calculez d'abord le cycle dans l'onglet 'Cycle mono-étagé'")
            h5_val = h4_val = v1_val = rend_vol_val = puissance_frigo_val = "---"
        else:
            resultats = st.session_state.resultats
            points = resultats['points']
            perf = resultats['performance']

            # Récupérer les valeurs du cycle
            h5_val = points['5']['H'] if points['5']['H'] is not None else None
            h4_val = points['4']['H'] if points['4']['H'] is not None else None
            v1_val = points['1']['V'] if points['1']['V'] is not None else None
            rend_vol_val = st.session_state.get('rendement_vol', 0.85)
            puissance_frigo_val = perf.get('puissance_frigorifique', 0)

            # Formater les valeurs pour l'affichage
            h5_display = f"{h5_val:.2f}" if h5_val else "---"
            h4_display = f"{h4_val:.2f}" if h4_val else "---"
            v1_display = f"{v1_val:.6f}" if v1_val else "---"
            rend_vol_display = f"{rend_vol_val:.4f}" if rend_vol_val else "---"
            puissance_frigo_display = f"{puissance_frigo_val:.2f}" if puissance_frigo_val else "---"

            # Afficher dans des cartes
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.markdown(f"""
                    <div style="background: #e3f2fd; border-left: 4px solid #1976d2; padding: 8px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 11px; color: #666;">h5 (kJ/kg)</div>
                        <div style="font-size: 16px; color: #1565c0; font-weight: bold;">{h5_display}</div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style="background: #e3f2fd; border-left: 4px solid #1976d2; padding: 8px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 11px; color: #666;">v1 (m³/kg)</div>
                        <div style="font-size: 16px; color: #1565c0; font-weight: bold;">{v1_display}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col_v2:
                st.markdown(f"""
                    <div style="background: #e3f2fd; border-left: 4px solid #1976d2; padding: 8px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 11px; color: #666;">h4 (kJ/kg)</div>
                        <div style="font-size: 16px; color: #1565c0; font-weight: bold;">{h4_display}</div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style="background: #e3f2fd; border-left: 4px solid #1976d2; padding: 8px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 11px; color: #666;">Rendement vol.</div>
                        <div style="font-size: 16px; color: #1565c0; font-weight: bold;">{rend_vol_display}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 8px; border-radius: 4px; margin: 4px 0;">
                    <div style="font-size: 11px; color: #666;">Puissance frigorifique (kW)</div>
                    <div style="font-size: 18px; color: #2e7d32; font-weight: bold;">{puissance_frigo_display}</div>
                </div>
            """, unsafe_allow_html=True)

    with col_catalogue:
        # SECTION 2 : Conditions catalogue
        st.markdown("""
            <div style="background: linear-gradient(135deg, #e53935 0%, #c62828 100%);
                        padding: 8px 12px; border-radius: 8px; margin-bottom: 10px;">
                <span style="color: white; font-weight: bold; font-size: 13px;">📋 CONDITIONS CATALOGUE</span>
            </div>
        """, unsafe_allow_html=True)

        # Calculer le rendement vol catalogue suggéré AVANT la création du widget
        # Supprimer la clé pour forcer le recalcul avec les températures actuelles
        if 'rendement_vol_catalogue' in st.session_state:
            del st.session_state['rendement_vol_catalogue']

        try:
            fluide_cat_key = st.session_state.get('fluide_catalogue', st.session_state.fluide)
            tevap_cat = st.session_state.get('tevap_catalogue', -10.0)
            tcond_cat = st.session_state.get('tcond_catalogue', 45.0)

            fluide_cat = obtenir_fluide_coolprop(fluide_cat_key)
            tevap_k = tevap_cat + 273.15
            tcond_k = tcond_cat + 273.15

            pression_evap_pa = PropsSI('P', 'T', tevap_k, 'Q', 1, fluide_cat)
            pression_cond_pa = PropsSI('P', 'T', tcond_k, 'Q', 0, fluide_cat)

            if pression_evap_pa > 0:
                taux_compression_cat = pression_cond_pa / pression_evap_pa
                rendement_vol_suggere = 1 - (0.04 * taux_compression_cat)
                rendement_vol_suggere = max(0.3, min(0.98, rendement_vol_suggere))
                st.session_state.rendement_vol_catalogue = round(rendement_vol_suggere, 2)
            else:
                st.session_state.rendement_vol_catalogue = 0.78
        except:
            st.session_state.rendement_vol_catalogue = 0.78

        col_cat1, col_cat2 = st.columns(2)

        with col_cat1:
            fluide_catalogue = st.selectbox(
                "Fluide catalogue",
                FLUIDES,
                index=FLUIDES.index(st.session_state.fluide) if st.session_state.fluide in FLUIDES else 0,
                key='fluide_catalogue'
            )
            tevap_catalogue = st.number_input(
                "t évap catalogue [°C]",
                value=st.session_state.get('tevap_catalogue', -10.0),
                key='tevap_catalogue',
                format="%.1f",
                step=1.0,
                help="Température de rosée (dew) pour les mélanges"
            )
            tcond_catalogue = st.number_input(
                "t cond catalogue [°C]",
                value=st.session_state.get('tcond_catalogue', 45.0),
                key='tcond_catalogue',
                format="%.1f",
                step=1.0,
                help="Température de bulle (bubble) pour les mélanges"
            )

        with col_cat2:
            surchauffe_catalogue = st.number_input(
                "Surchauffe catalogue [K]",
                value=st.session_state.get('surchauffe_catalogue', 0.0),
                key='surchauffe_catalogue',
                format="%.0f",
                step=1.0,
                min_value=0.0
            )
            sous_ref_catalogue = st.number_input(
                "Sous-refroid. catalogue [K]",
                value=st.session_state.get('sous_ref_catalogue', 0.0),
                key='sous_ref_catalogue',
                format="%.0f",
                step=1.0,
                min_value=0.0
            )
            rendement_vol_catalogue = st.number_input(
                "Rendement vol' catalogue [-]",
                value=st.session_state.get('rendement_vol_catalogue', 0.78),
                key='rendement_vol_catalogue',
                format="%.2f",
                step=0.01,
                min_value=0.1,
                max_value=1.0,
                help="Calculé automatiquement: ηvol' = 1 - 0.04 × τ (modifiable)"
            )

        # Bouton calculer valeurs catalogue
        if st.button("🔄 Calculer valeurs catalogue", use_container_width=True, key='btn_calc_catalogue'):
            try:
                fluide_cat = obtenir_fluide_coolprop(fluide_catalogue)
                tevap_k = tevap_catalogue + 273.15
                tcond_k = tcond_catalogue + 273.15

                # Pressions de saturation
                pression_evap_pa = PropsSI('P', 'T', tevap_k, 'Q', 1, fluide_cat)
                pression_cond_pa = PropsSI('P', 'T', tcond_k, 'Q', 0, fluide_cat)

                # Calcul et affichage du rendement vol suggéré (info seulement)
                if pression_evap_pa > 0:
                    taux_compression_cat = pression_cond_pa / pression_evap_pa
                    rendement_vol_cat_suggere = 1 - (0.04 * taux_compression_cat)
                    rendement_vol_cat_suggere = max(0.3, min(0.98, rendement_vol_cat_suggere))
                    st.info(f"💡 ηvol' suggéré (τ={taux_compression_cat:.2f}) : **{rendement_vol_cat_suggere:.2f}**")

                # Point 1 catalogue (aspiration)
                temp_point1_k = tevap_k + surchauffe_catalogue
                if abs(surchauffe_catalogue) < 0.01:
                    h1_cat = PropsSI('H', 'P', pression_evap_pa, 'Q', 1, fluide_cat) / 1000
                    v1_cat = 1 / PropsSI('D', 'P', pression_evap_pa, 'Q', 1, fluide_cat)
                else:
                    h1_cat = PropsSI('H', 'P', pression_evap_pa, 'T', temp_point1_k, fluide_cat) / 1000
                    v1_cat = 1 / PropsSI('D', 'P', pression_evap_pa, 'T', temp_point1_k, fluide_cat)

                # Point 3 catalogue (sortie condenseur)
                temp_point3_k = tcond_k - sous_ref_catalogue
                if abs(sous_ref_catalogue) < 0.01:
                    h3_cat = PropsSI('H', 'P', pression_cond_pa, 'Q', 0, fluide_cat) / 1000
                else:
                    h3_cat = PropsSI('H', 'P', pression_cond_pa, 'T', temp_point3_k, fluide_cat) / 1000

                # h4 catalogue = h3 (détente isenthalpique)
                h4_cat = h3_cat

                # Stocker les valeurs
                st.session_state.h1_catalogue = h1_cat
                st.session_state.h4_catalogue = h4_cat
                st.session_state.v1_catalogue = v1_cat

                st.success("✅ Valeurs catalogue calculées (ηvol' mis à jour automatiquement)")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")

        # Afficher les valeurs catalogue calculées
        if st.session_state.h1_catalogue is not None:
            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                st.markdown(f"""
                    <div style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 6px; border-radius: 4px;">
                        <div style="font-size: 10px; color: #666;">h'1 (kJ/kg)</div>
                        <div style="font-size: 14px; color: #e65100; font-weight: bold;">{st.session_state.h1_catalogue:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_res2:
                st.markdown(f"""
                    <div style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 6px; border-radius: 4px;">
                        <div style="font-size: 10px; color: #666;">h'4 (kJ/kg)</div>
                        <div style="font-size: 14px; color: #e65100; font-weight: bold;">{st.session_state.h4_catalogue:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_res3:
                st.markdown(f"""
                    <div style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 6px; border-radius: 4px;">
                        <div style="font-size: 10px; color: #666;">v'1 (m³/kg)</div>
                        <div style="font-size: 14px; color: #e65100; font-weight: bold;">{st.session_state.v1_catalogue:.6f}</div>
                    </div>
                """, unsafe_allow_html=True)

    # SECTION 3 : Calcul du coefficient Kcat
    st.markdown("""
        <div style="background: linear-gradient(135deg, #7b1fa2 0%, #6a1b9a 100%);
                    padding: 8px 12px; border-radius: 8px; margin: 15px 0 10px 0;">
            <span style="color: white; font-weight: bold; font-size: 13px;">🔢 CALCUL DU COEFFICIENT CATALOGUE (Kcat)</span>
        </div>
    """, unsafe_allow_html=True)

    # Afficher la formule
    st.markdown("""
        <div style="background: #f5f5f5; padding: 10px; border-radius: 8px; margin: 10px 0; text-align: center;">
            <span style="font-size: 14px; font-weight: bold;">
                Kcat = [(h'1 - h'4) / (h5 - h4)] × [v1 / v'1] × [ηvol' / ηvol]
            </span>
        </div>
    """, unsafe_allow_html=True)

    # Bouton calculer Kcat
    if st.button("🔄 Calculer Kcat et Puissance catalogue", type="primary", use_container_width=True, key='btn_calc_kcat'):
        try:
            # Vérifier que toutes les valeurs sont disponibles
            if st.session_state.resultats is None:
                st.error("❌ Calculez d'abord le cycle dans l'onglet 'Cycle mono-étagé'")
            elif st.session_state.h1_catalogue is None:
                st.error("❌ Calculez d'abord les valeurs catalogue")
            else:
                resultats = st.session_state.resultats
                points = resultats['points']
                perf = resultats['performance']

                h5 = points['5']['H']
                h4 = points['4']['H']
                v1 = points['1']['V']
                rend_vol = st.session_state.get('rendement_vol', 0.85)
                puissance_frigo = perf.get('puissance_frigorifique', 0)

                h1_cat = st.session_state.h1_catalogue
                h4_cat = st.session_state.h4_catalogue
                v1_cat = st.session_state.v1_catalogue
                rend_vol_cat = st.session_state.get('rendement_vol_catalogue', 1.0)

                # Calcul des termes
                delta_h_cat = h1_cat - h4_cat
                delta_h_reel = h5 - h4

                if abs(delta_h_reel) < 1e-6:
                    st.error("❌ Division par zéro: h5 - h4 = 0")
                elif abs(v1_cat) < 1e-9:
                    st.error("❌ Division par zéro: v'1 = 0")
                elif abs(rend_vol) < 1e-6:
                    st.error("❌ Division par zéro: ηvol = 0")
                else:
                    terme1 = delta_h_cat / delta_h_reel
                    terme2 = v1 / v1_cat
                    terme3 = rend_vol_cat / rend_vol

                    kcat = terme1 * terme2 * terme3
                    puissance_cat = puissance_frigo * kcat

                    st.session_state.kcat = kcat
                    st.session_state.puissance_catalogue = puissance_cat

                    st.success(f"✅ Kcat = {kcat:.4f} | Puissance catalogue = {puissance_cat:.2f} kW")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")

    # Afficher les résultats Kcat
    col_kcat, col_pcat = st.columns(2)

    with col_kcat:
        kcat_display = f"{st.session_state.kcat:.4f}" if st.session_state.kcat else "---"
        st.markdown(f"""
            <div style="background: #f3e5f5; border: 2px solid #9c27b0; padding: 15px; border-radius: 8px; text-align: center;">
                <div style="font-size: 12px; color: #666; font-weight: bold;">Coefficient Kcat</div>
                <div style="font-size: 24px; color: #7b1fa2; font-weight: bold;">{kcat_display}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_pcat:
        pcat_display = f"{st.session_state.puissance_catalogue:.2f} kW" if st.session_state.puissance_catalogue else "---"
        st.markdown(f"""
            <div style="background: #e8f5e9; border: 2px solid #4caf50; padding: 15px; border-radius: 8px; text-align: center;">
                <div style="font-size: 12px; color: #666; font-weight: bold;">Puissance catalogue</div>
                <div style="font-size: 24px; color: #2e7d32; font-weight: bold;">{pcat_display}</div>
            </div>
        """, unsafe_allow_html=True)

    # SECTION 4 : Calcul puissance réelle à partir de la puissance catalogue choisie
    st.markdown("""
        <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
                    padding: 8px 12px; border-radius: 8px; margin: 15px 0 10px 0;">
            <span style="color: white; font-weight: bold; font-size: 13px;">⚡ PUISSANCE RÉELLE À PARTIR DU CATALOGUE</span>
        </div>
    """, unsafe_allow_html=True)

    col_puiss1, col_puiss2 = st.columns(2)

    with col_puiss1:
        puissance_choisie = st.number_input(
            "Puissance choisie dans le catalogue [kW]",
            value=st.session_state.get('puissance_choisie_catalogue', 0.0),
            key='puissance_choisie_catalogue',
            format="%.2f",
            min_value=0.0,
            help="Entrez la puissance frigorifique du compresseur lu dans le catalogue constructeur"
        )

    with col_puiss2:
        # Calculer la puissance réelle
        if st.session_state.kcat and st.session_state.kcat > 0 and puissance_choisie > 0:
            puissance_reelle = puissance_choisie / st.session_state.kcat
            st.markdown(f"""
                <div style="background: #fff8e1; border: 2px solid #ffc107; padding: 15px; border-radius: 8px; text-align: center; margin-top: 25px;">
                    <div style="font-size: 12px; color: #666; font-weight: bold;">Puissance frigorifique réelle</div>
                    <div style="font-size: 24px; color: #ff6f00; font-weight: bold;">{puissance_reelle:.2f} kW</div>
                    <div style="font-size: 10px; color: #999;">= P_catalogue / Kcat</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="background: #f5f5f5; border: 2px solid #bdbdbd; padding: 15px; border-radius: 8px; text-align: center; margin-top: 25px;">
                    <div style="font-size: 12px; color: #666; font-weight: bold;">Puissance frigorifique réelle</div>
                    <div style="font-size: 24px; color: #9e9e9e; font-weight: bold;">---</div>
                    <div style="font-size: 10px; color: #999;">Calculez Kcat et entrez une puissance</div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Note explicative
    st.info("""
    **Comment utiliser le coefficient Kcat :**
    1. Calculez votre cycle frigorifique dans l'onglet 'Cycle mono-étagé'
    2. Entrez les conditions catalogue du fabricant (généralement : t_evap, t_cond, surchauffe=0, sous-refroid=0, ηvol'=1)
    3. Calculez les valeurs catalogue, puis Kcat
    4. Entrez la puissance lue dans le catalogue constructeur pour obtenir la puissance réelle à vos conditions
    """)

elif onglet_selectionne == "Bi-étagé":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0f4c75 0%, #1b6ca8 100%);
                    padding: 10px 15px; border-radius: 10px; margin-bottom: 15px;">
            <span style="color: white; font-weight: bold; font-size: 15px;">
                ❄️❄️ CYCLE BI-ÉTAGÉ — Injection totale avec bouteille intermédiaire
            </span>
        </div>
    """, unsafe_allow_html=True)

    # Déclenchement du calcul
    if st.session_state.get('bi_calculer', False):
        res = calculer_cycle_bietage()
        if res:
            st.session_state.bi_resultats = res
            st.success("Calcul réussi !")
        st.session_state.bi_calculer = False

    # ── SÉLECTEUR D'ARCHITECTURE ─────────────────────────────────────────────
    _mode_options = ['Injection totale', 'Injection totale avec bouteille BP', 'Injection partielle']
    _mode_colors  = {'Injection totale': '#0f4c75', 'Injection totale avec bouteille BP': '#1a4a6b',
                     'Injection partielle': '#5c3317'}
    _mode_icons   = {'Injection totale': '🔀', 'Injection totale avec bouteille BP': '🔀🔁',
                     'Injection partielle': '💉'}
    _mode_desc    = {
        'Injection totale':                   'Tout le liquide du condenseur passe par la bouteille intermédiaire — bilan: r = (h₂−h₇)/(h₃−h₅)',
        'Injection totale avec bouteille BP': 'Injection totale + bouteille BP avec pompe de recirculation côté basse pression — même bilan massique',
        'Injection partielle':                'Fraction du liquide injectée via échangeur à plaques — bilan: r = 1 + (h₅−h₇)/(h″−h₅)',
    }

    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        st.selectbox(
            "Configuration du système d'intercooler",
            _mode_options,
            index=_mode_options.index(st.session_state.bi_mode) if st.session_state.bi_mode in _mode_options else 0,
            key='bi_mode',
            help="Choisir l'architecture thermodynamique du cycle bi-étagé"
        )
    with col_m2:
        _cur_mode = st.session_state.bi_mode
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, {_mode_colors[_cur_mode]} 0%, #1a2940 100%);
                        border-radius: 8px; padding: 10px 14px; margin-top: 4px;">
                <span style="color: white; font-weight: bold; font-size: 13px;">
                    {_mode_icons[_cur_mode]} {_cur_mode}
                </span><br>
                <span style="color: #cbd5e1; font-size: 11px;">{_mode_desc[_cur_mode]}</span>
            </div>
        """, unsafe_allow_html=True)

    # ── LIGNE FLUIDE + COLONNES PRINCIPALES ──────────────────────────────────
    col_left, col_right = st.columns([1.6, 2])

    with col_left:
        # Fluide (compact, en haut)
        col_fl, col_fl2 = st.columns([1, 1])
        with col_fl:
            st.markdown("<div style='font-size:11px;color:#764ba2;font-weight:bold;'>🧪 Fluide frigorigène</div>",
                        unsafe_allow_html=True)
            st.selectbox("Fluide", FLUIDES,
                         index=FLUIDES.index(st.session_state.bi_fluide) if st.session_state.bi_fluide in FLUIDES else 0,
                         key='bi_fluide', label_visibility="collapsed")
        with col_fl2:
            # Pression intermédiaire (pi auto affiché ici en permanence si auto)
            po_v_top = st.session_state.get('bi_po')
            pk_v_top = st.session_state.get('bi_pk')
            if po_v_top and pk_v_top and po_v_top > 0 and pk_v_top > 0:
                _pi_top = (po_v_top * pk_v_top) ** 0.5
                try:
                    _f_top = obtenir_fluide_coolprop(st.session_state.bi_fluide)
                    _ti_top = PropsSI('T', 'P', _pi_top * 1e5, 'Q', 0, _f_top) - 273.15
                    st.markdown(f"""<div style="background:#e0f2f1;border-left:3px solid #00897b;
                        padding:5px 8px;border-radius:4px;margin-top:20px;font-size:12px;">
                        <b style="color:#004d40;">pi = {_pi_top:.3f} bar &nbsp;|&nbsp; ti = {_ti_top:.1f} °C</b></div>""",
                        unsafe_allow_html=True)
                except:
                    pass

        st.markdown("<hr style='margin:6px 0;border-color:#e2e8f0;'>", unsafe_allow_html=True)

        # Évaporation / Condensation
        col_ev, col_cd = st.columns(2)

        with col_ev:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
                            padding: 6px 10px; border-radius: 8px; margin-bottom: 8px;">
                    <span style="color: white; font-weight: bold; font-size: 12px;">❄️ ÉVAPORATION (BP)</span>
                </div>
            """, unsafe_allow_html=True)

            def _maj_rendements_bi():
                """Recalcule ηvol BP et HP à partir de p0, pi, pk."""
                try:
                    po_v = st.session_state.get('bi_po')
                    pk_v = st.session_state.get('bi_pk')
                    if not (po_v and pk_v and po_v > 0 and pk_v > 0):
                        return
                    # Pression intermédiaire
                    if st.session_state.get('bi_pi_mode') == 'Pression pi [bar]':
                        pi_v = st.session_state.get('bi_pi')
                    elif st.session_state.get('bi_pi_mode') == 'Température ti [°C]':
                        pi_v = st.session_state.get('bi_pi')
                    else:
                        pi_v = (po_v * pk_v) ** 0.5
                    if not pi_v or pi_v <= 0:
                        pi_v = (po_v * pk_v) ** 0.5
                    eta_bp = 1 - 0.04 * (pi_v / po_v)
                    eta_hp = 1 - 0.04 * (pk_v / pi_v)
                    st.session_state.bi_eta_vol_bp = round(max(0.3, min(0.98, eta_bp)), 3)
                    st.session_state.bi_eta_vol_hp = round(max(0.3, min(0.98, eta_hp)), 3)
                except:
                    pass

            def _on_bi_to():
                try:
                    to_v = st.session_state.get('bi_to')
                    if to_v is not None:
                        f = obtenir_fluide_coolprop(st.session_state.bi_fluide)
                        for q in [1, 0.5, 0]:
                            try:
                                p = PropsSI('P', 'T', to_v + 273.15, 'Q', q, f)
                                if p:
                                    st.session_state.bi_po = p / 1e5
                                    break
                            except:
                                continue
                        _maj_rendements_bi()
                except:
                    pass

            def _on_bi_po():
                try:
                    po_v = st.session_state.get('bi_po')
                    if po_v and po_v > 0:
                        f = obtenir_fluide_coolprop(st.session_state.bi_fluide)
                        for q in [1, 0.5, 0]:
                            try:
                                t = PropsSI('T', 'P', po_v * 1e5, 'Q', q, f)
                                if t:
                                    st.session_state.bi_to = t - 273.15
                                    break
                            except:
                                continue
                        _maj_rendements_bi()
                except:
                    pass

            st.number_input("t₀ [°C]", value=st.session_state.get('bi_to'), key='bi_to',
                            format="%.2f", on_change=_on_bi_to)
            st.number_input("p₀ [bar abs]", value=st.session_state.get('bi_po'), key='bi_po',
                            format="%.3f", on_change=_on_bi_po)
            if st.session_state.get('bi_mode') != 'Injection partielle':
                st.number_input("Surchauffe [K]", value=st.session_state.get('bi_surchauffe', 5.0),
                                key='bi_surchauffe', min_value=0.0, max_value=30.0, step=1.0, format="%.0f")

        with col_cd:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #e53935 0%, #c62828 100%);
                            padding: 6px 10px; border-radius: 8px; margin-bottom: 8px;">
                    <span style="color: white; font-weight: bold; font-size: 12px;">🔥 CONDENSATION (HP)</span>
                </div>
            """, unsafe_allow_html=True)

            def _on_bi_tc():
                try:
                    tc_v = st.session_state.get('bi_tc')
                    if tc_v is not None:
                        f = obtenir_fluide_coolprop(st.session_state.bi_fluide)
                        for q in [0, 0.5, 1]:
                            try:
                                p = PropsSI('P', 'T', tc_v + 273.15, 'Q', q, f)
                                if p:
                                    st.session_state.bi_pk = p / 1e5
                                    break
                            except:
                                continue
                        _maj_rendements_bi()
                except:
                    pass

            def _on_bi_pk():
                try:
                    pk_v = st.session_state.get('bi_pk')
                    if pk_v and pk_v > 0:
                        f = obtenir_fluide_coolprop(st.session_state.bi_fluide)
                        for q in [0, 0.5, 1]:
                            try:
                                t = PropsSI('T', 'P', pk_v * 1e5, 'Q', q, f)
                                if t:
                                    st.session_state.bi_tc = t - 273.15
                                    break
                            except:
                                continue
                        _maj_rendements_bi()
                except:
                    pass

            st.number_input("tₖ [°C]", value=st.session_state.get('bi_tc'), key='bi_tc',
                            format="%.2f", on_change=_on_bi_tc)
            st.number_input("pₖ [bar abs]", value=st.session_state.get('bi_pk'), key='bi_pk',
                            format="%.3f", on_change=_on_bi_pk)
            st.number_input("Sous-refroid. [K]", value=st.session_state.get('bi_sous_refroid', 5.0),
                            key='bi_sous_refroid', min_value=0.0, max_value=30.0, step=1.0, format="%.0f")

        # ── pi + rendements (ligne compacte) ─────────────────────────────────
        st.markdown("<div style='font-size:11px;color:#00695c;font-weight:bold;margin-top:4px;'>🔀 Pression intermédiaire</div>",
                    unsafe_allow_html=True)
        col_pi1, col_pi2 = st.columns([1, 1])
        with col_pi1:
            st.selectbox("Mode pi", ['Auto (√(p₀×pₖ))', 'Température ti [°C]', 'Pression pi [bar]'],
                         key='bi_pi_mode', label_visibility="collapsed")
        with col_pi2:
            if st.session_state.bi_pi_mode == 'Température ti [°C]':
                def _on_bi_ti():
                    try:
                        ti_v = st.session_state.get('bi_ti')
                        if ti_v is not None:
                            f = obtenir_fluide_coolprop(st.session_state.bi_fluide)
                            for q in [0, 0.5, 1]:
                                try:
                                    p = PropsSI('P', 'T', ti_v + 273.15, 'Q', q, f)
                                    if p:
                                        st.session_state.bi_pi = p / 1e5
                                        break
                                except: continue
                            _maj_rendements_bi()
                    except: pass
                st.number_input("ti [°C]", value=st.session_state.get('bi_ti'), key='bi_ti',
                                format="%.2f", on_change=_on_bi_ti)
            elif st.session_state.bi_pi_mode == 'Pression pi [bar]':
                st.number_input("pi [bar abs]", value=st.session_state.get('bi_pi'), key='bi_pi',
                                format="%.3f", on_change=_maj_rendements_bi)
            else:
                st.markdown("<div style='font-size:11px;color:#777;margin-top:28px;'>calculée automatiquement ↑</div>",
                            unsafe_allow_html=True)

        # Rendements (4 champs sur 2 lignes × 2 colonnes)
        st.markdown("<div style='font-size:11px;color:#6a1b9a;font-weight:bold;margin-top:4px;'>⚙️ Rendements compresseurs</div>",
                    unsafe_allow_html=True)
        cr1, cr2, cr3, cr4 = st.columns(4)
        with cr1:
            st.number_input("ηvol BP", value=st.session_state.get('bi_eta_vol_bp', 0.78),
                            key='bi_eta_vol_bp', min_value=0.1, max_value=1.0, step=0.01, format="%.2f",
                            help="ηvol_BP = 1 − 0.04 × (pi/p₀)")
        with cr2:
            st.number_input("ηis BP", value=st.session_state.get('bi_eta_is_bp', 0.75),
                            key='bi_eta_is_bp', min_value=0.1, max_value=1.0, step=0.01, format="%.2f",
                            help="Rendement isentropique BP")
        with cr3:
            st.number_input("ηvol HP", value=st.session_state.get('bi_eta_vol_hp', 0.78),
                            key='bi_eta_vol_hp', min_value=0.1, max_value=1.0, step=0.01, format="%.2f",
                            help="ηvol_HP = 1 − 0.04 × (pₖ/pi)")
        with cr4:
            st.number_input("ηis HP", value=st.session_state.get('bi_eta_is_hp', 0.75),
                            key='bi_eta_is_hp', min_value=0.1, max_value=1.0, step=0.01, format="%.2f",
                            help="Rendement isentropique HP")

        # ── Dimensionnement + options ─────────────────────────────────────────
        st.markdown("<div style='font-size:11px;color:#2e7d32;font-weight:bold;margin-top:4px;'>📐 Dimensionnement</div>",
                    unsafe_allow_html=True)
        col_dim1, col_dim2, col_dim3 = st.columns([1.2, 1, 1])
        with col_dim1:
            st.selectbox("Donnée d'entrée",
                         ['Puissance frigorifique [kW]', 'Volume balayé BP [m³/h]'],
                         key='bi_type_entree', label_visibility="collapsed")
        with col_dim2:
            label_entree = "Q frigo BP [kW]" if st.session_state.bi_type_entree == 'Puissance frigorifique [kW]' else "Vb BP [m³/h]"
            fmt = "%.2f" if st.session_state.bi_type_entree == 'Puissance frigorifique [kW]' else "%.1f"
            st.number_input(label_entree, value=st.session_state.get('bi_valeur_entree', 0.0),
                            key='bi_valeur_entree', min_value=0.0, format=fmt)
        with col_dim3:
            if st.session_state.bi_mode in ('Injection totale', 'Injection totale avec bouteille BP'):
                st.number_input("Q frigo MP [kW]",
                    value=st.session_state.get('bi_q_evap_mp', 0.0),
                    key='bi_q_evap_mp', min_value=0.0, step=1.0, format="%.2f",
                    help="Puissance de l'évaporateur intermédiaire à pi (0 = mono-évap)")
            elif st.session_state.bi_mode == 'Sous-refroidisseur (EVI)':
                st.number_input("ΔT HX [K]",
                    value=st.session_state.get('bi_dt_sub_hx', 5.0),
                    key='bi_dt_sub_hx', min_value=1.0, max_value=30.0, step=1.0, format="%.0f",
                    help="Sous-refroidissement échangeur EVI")

        # Ligne dédiée injection partielle (pincement + surchauffe) — hors des colonnes étroites
        if st.session_state.bi_mode == 'Injection partielle':
            col_ip1, col_ip2, col_ip3 = st.columns([1, 1, 2])
            with col_ip1:
                st.number_input("Pincement T₇−ti [K]",
                    value=st.session_state.get('bi_dt_pincement', 5.0),
                    key='bi_dt_pincement', min_value=1.0, max_value=30.0, step=1.0, format="%.0f",
                    help="T₇ = ti + Δt_pincement (sortie liquide échangeur)")
            with col_ip2:
                st.number_input("Surchauffe évap BP [K]",
                    value=st.session_state.get('bi_surchauffe_evap_bp', 5.0),
                    key='bi_surchauffe_evap_bp', min_value=0.0, max_value=30.0, step=1.0, format="%.0f",
                    help="Surchauffe sortie évap BP — point 9")

        # ── Pompe (expander pour économiser la place) ─────────────────────────
        if st.session_state.bi_mode in ('Injection totale', 'Injection totale avec bouteille BP'):
            with st.expander("🔧 Pompe de circulation", expanded=st.session_state.get('bi_has_pump', False)):
                st.checkbox("Activer la pompe", value=st.session_state.get('bi_has_pump', False),
                            key='bi_has_pump', help="Inclure la puissance pompe dans le COP")
                if st.session_state.bi_has_pump:
                    cp1, cp2, cp3, cp4 = st.columns(4)
                    with cp1:
                        st.number_input("n recirculat.", value=st.session_state.get('bi_pump_n', 3.0),
                                        key='bi_pump_n', min_value=1.0, max_value=20.0, step=0.5, format="%.1f",
                                        help="ṁ_pompe = n × ṁ_MP")
                    with cp2:
                        st.number_input("ΔP [bar]", value=st.session_state.get('bi_pump_dp', 0.5),
                                        key='bi_pump_dp', min_value=0.01, max_value=20.0, step=0.1, format="%.2f",
                                        help="Perte de charge totale du circuit")
                    with cp3:
                        st.number_input("η pompe", value=st.session_state.get('bi_pump_eta', 0.60),
                                        key='bi_pump_eta', min_value=0.10, max_value=1.0, step=0.05, format="%.2f",
                                        help="Rendement hydraulique + mécanique")
                    with cp4:
                        st.number_input("H statique [m]", value=st.session_state.get('bi_pump_height', 2.0),
                                        key='bi_pump_height', min_value=0.0, max_value=20.0, step=0.5, format="%.1f",
                                        help="Vérification NPSH (min 1,5 m)")

        # ── Boutons ───────────────────────────────────────────────────────────
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔄 CALCULER", type="primary", use_container_width=True, key='btn_bi_calc'):
                st.session_state.bi_calculer = True
                st.rerun()
        with col_btn2:
            if st.button("🗑️ Effacer", use_container_width=True, key='btn_bi_eff'):
                for k in ['bi_to', 'bi_po', 'bi_tc', 'bi_pk', 'bi_ti', 'bi_pi',
                          'bi_valeur_entree', 'bi_resultats']:
                    if k in st.session_state:
                        del st.session_state[k]
                st.session_state.bi_surchauffe = 5.0
                st.session_state.bi_sous_refroid = 5.0
                st.session_state.bi_eta_vol_bp = 0.78
                st.session_state.bi_eta_is_bp = 0.75
                st.session_state.bi_eta_vol_hp = 0.78
                st.session_state.bi_eta_is_hp = 0.75
                st.session_state.bi_has_pump = False
                st.session_state.bi_pump_power = 0.0
                st.session_state.bi_pump_n = 3.0
                st.session_state.bi_pump_dp = 0.5
                st.session_state.bi_pump_eta = 0.60
                st.session_state.bi_pump_height = 2.0
                st.session_state.bi_dt_sub_hx = 5.0
                st.session_state.bi_q_evap_mp = 0.0
                st.rerun()

    with col_right:
        # Schéma de l'installation selon le mode
        _cur_bi_mode = st.session_state.get('bi_mode', 'Injection totale')
        if _cur_bi_mode == 'Injection totale':
            try:
                _img_path = resource_path("schemaFluBiEtageInjTotalePompe1.png")
                if os.path.exists(_img_path):
                    _res_bi = st.session_state.get('bi_resultats')
                    if _res_bi and _res_bi.get('performance'):
                        _schema_img = superposer_volumes_schema(_img_path, _res_bi['performance'])
                    else:
                        _schema_img = Image.open(_img_path)
                    st.image(_schema_img, use_container_width=True)
            except Exception:
                pass
        elif _cur_bi_mode == 'Injection totale avec bouteille BP':
            try:
                _img_path = resource_path("schemaFluBiEtageInjTotalePompeEcHPlaque.png")
                if os.path.exists(_img_path):
                    _res_bi = st.session_state.get('bi_resultats')
                    if _res_bi and _res_bi.get('performance'):
                        _schema_img = superposer_schema_bouteille_bp(_img_path, _res_bi['performance'])
                    else:
                        _schema_img = Image.open(_img_path)
                    st.image(_schema_img, use_container_width=True)
            except Exception:
                pass
        elif _cur_bi_mode == 'Injection partielle':
            try:
                _img_path = resource_path("schemaFluInjPartielleEcgPlaque.png")
                if os.path.exists(_img_path):
                    _res_bi = st.session_state.get('bi_resultats')
                    if _res_bi and _res_bi.get('performance'):
                        _schema_img = superposer_schema_inj_partielle(_img_path, _res_bi['performance'])
                    else:
                        _schema_img = Image.open(_img_path)
                    st.image(_schema_img, use_container_width=True)
            except Exception:
                pass

        # Récap conditions — affiché dès qu'au moins une condition BP ou HP est saisie
        _has_bp = st.session_state.get('bi_to') is not None or st.session_state.get('bi_po') is not None
        _has_hp = st.session_state.get('bi_tc') is not None or st.session_state.get('bi_pk') is not None
        if _has_bp or _has_hp:
            st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
            col_r1, col_r2 = st.columns(2)
            po_v = st.session_state.get('bi_po')
            to_v = st.session_state.get('bi_to')
            pk_v = st.session_state.get('bi_pk')
            tc_v = st.session_state.get('bi_tc')
            with col_r1:
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                                border: 2px solid #1976d2; border-radius: 8px; padding: 10px;">
                        <div style="font-size: 11px; color: #1565c0; font-weight: bold;">❄️ BASSE PRESSION</div>
                        <div style="font-size: 16px; color: #0d47a1; font-weight: bold;">
                            t₀ = {f"{to_v:.1f}" if to_v is not None else "---"} °C
                        </div>
                        <div style="font-size: 16px; color: #0d47a1; font-weight: bold;">
                            p₀ = {f"{po_v:.3f}" if po_v is not None else "---"} bar
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col_r2:
                pi_auto = None
                if po_v and pk_v and po_v > 0 and pk_v > 0:
                    pi_auto = (po_v * pk_v) ** 0.5
                pi_show = st.session_state.get('bi_pi', pi_auto)
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
                                border: 2px solid #d32f2f; border-radius: 8px; padding: 10px;">
                        <div style="font-size: 11px; color: #c62828; font-weight: bold;">🔥 HAUTE PRESSION</div>
                        <div style="font-size: 16px; color: #b71c1c; font-weight: bold;">
                            tₖ = {f"{tc_v:.1f}" if tc_v is not None else "---"} °C
                        </div>
                        <div style="font-size: 16px; color: #b71c1c; font-weight: bold;">
                            pₖ = {f"{pk_v:.3f}" if pk_v is not None else "---"} bar
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            if pi_show:
                try:
                    f_cp = obtenir_fluide_coolprop(st.session_state.bi_fluide)
                    t_int_disp = PropsSI('T', 'P', pi_show * 1e5, 'Q', 0, f_cp) - 273.15
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%);
                                    border: 2px solid #00897b; border-radius: 8px; padding: 10px; margin-top: 8px;">
                            <div style="font-size: 11px; color: #004d40; font-weight: bold;">🔀 PRESSION INTERMÉDIAIRE</div>
                            <div style="font-size: 16px; color: #004d40; font-weight: bold;">
                                ti = {t_int_disp:.1f} °C &nbsp;|&nbsp; pi = {pi_show:.3f} bar
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                except:
                    pass

    # ──────────────────────────────────────────────────────────
    # LIGNE 2 : Résultats performance + Tableau des points
    # ──────────────────────────────────────────────────────────
    st.markdown("---")

    if st.session_state.bi_resultats:
        res = st.session_state.bi_resultats
        perf = res['performance']
        pts = res['points']
        inter = res['intermediate']

        col_perf, col_tab = st.columns([1, 1])

        with col_perf:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
                            padding: 8px 12px; border-radius: 8px; margin-bottom: 10px;">
                    <span style="color: white; font-weight: bold; font-size: 13px;">📊 RÉSULTATS</span>
                </div>
            """, unsafe_allow_html=True)

            # Puissances frigorifique / calorifique
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                _q_evap_mp_kw = perf.get('q_evap_mp', 0.0)
                _q_label_bp = f"dont BP : {perf['q_evap_bp']:.2f} kW | MP : {_q_evap_mp_kw:.2f} kW" if _q_evap_mp_kw > 0 else ""
                st.markdown(f"""
                    <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 10px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">❄️ Puissance frigorifique totale</div>
                        <div style="font-size: 20px; color: #2e7d32; font-weight: bold;">{perf['q_evap']:.2f} kW</div>
                        {'<div style="font-size: 10px; color: #555;">' + _q_label_bp + '</div>' if _q_label_bp else ''}
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style="background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 10px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">⚡ W BP</div>
                        <div style="font-size: 20px; color: #7b1fa2; font-weight: bold;">{perf['w_bp']:.2f} kW</div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style="background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 10px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">⚡ W HP</div>
                        <div style="font-size: 20px; color: #7b1fa2; font-weight: bold;">{perf['w_hp']:.2f} kW</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_r2:
                st.markdown(f"""
                    <div style="background: #ffebee; border-left: 4px solid #f44336; padding: 10px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">🔥 Puissance calorifique</div>
                        <div style="font-size: 20px; color: #c62828; font-weight: bold;">{perf['q_cond']:.2f} kW</div>
                    </div>
                """, unsafe_allow_html=True)
                cop_color = "#4caf50" if perf['cop'] >= 3 else ("#ff9800" if perf['cop'] >= 2 else "#f44336")
                st.markdown(f"""
                    <div style="background: #fff8e1; border-left: 4px solid #ff9800; padding: 10px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">🎯 COP</div>
                        <div style="font-size: 20px; color: {cop_color}; font-weight: bold;">{perf['cop']:.3f}</div>
                    </div>
                """, unsafe_allow_html=True)
                _pump_line = f'<div style="font-size:10px;color:#9e9e9e;">dont pompe: {perf["w_pump"]:.2f} kW</div>' if perf['w_pump'] > 0 else ''
                st.markdown(f"""
                    <div style="background: #fafafa; border-left: 4px solid #607d8b; padding: 10px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 11px; color: #666; font-weight: bold;">⚡ W total</div>
                        <div style="font-size: 18px; color: #37474f; font-weight: bold;">{perf['w_total']:.2f} kW</div>
                        {_pump_line}
                    </div>
                """, unsafe_allow_html=True)

            # Débits massiques
            st.markdown("""
                <div style="background: linear-gradient(135deg, #0f4c75 0%, #1b6ca8 100%);
                            padding: 6px 10px; border-radius: 8px; margin: 12px 0 8px 0;">
                    <span style="color: white; font-weight: bold; font-size: 12px;">💧 DÉBITS MASSIQUES</span>
                </div>
            """, unsafe_allow_html=True)

            _m_mp = perf.get('m_mp', 0.0)
            _ncols_m = 3 if _m_mp > 0 else 2
            _m_cols = st.columns(_ncols_m)
            with _m_cols[0]:
                st.markdown(f"""
                    <div style="background: #e3f2fd; border: 2px solid #1976d2; padding: 12px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; color: #1565c0; font-weight: bold;">💧 qm BP (ṁ BP)</div>
                        <div style="font-size: 20px; color: #0d47a1; font-weight: bold;">{perf['m_bp']*3600:.2f}</div>
                        <div style="font-size: 11px; color: #555;">kg/h</div>
                        <div style="font-size: 10px; color: #777; margin-top: 2px;">{perf['m_bp']:.5f} kg/s</div>
                    </div>
                """, unsafe_allow_html=True)
            if _m_mp > 0:
                with _m_cols[1]:
                    st.markdown(f"""
                        <div style="background: #e8f5e9; border: 2px solid #388e3c; padding: 12px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 11px; color: #2e7d32; font-weight: bold;">💧 qm MP (ṁ MP)</div>
                            <div style="font-size: 20px; color: #1b5e20; font-weight: bold;">{_m_mp*3600:.2f}</div>
                            <div style="font-size: 11px; color: #555;">kg/h</div>
                            <div style="font-size: 10px; color: #777; margin-top: 2px;">{_m_mp:.5f} kg/s</div>
                        </div>
                    """, unsafe_allow_html=True)
            with _m_cols[-1]:
                st.markdown(f"""
                    <div style="background: #ffebee; border: 2px solid #d32f2f; padding: 12px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; color: #c62828; font-weight: bold;">💧 qm HP (ṁ HP)</div>
                        <div style="font-size: 20px; color: #b71c1c; font-weight: bold;">{perf['m_hp']*3600:.2f}</div>
                        <div style="font-size: 11px; color: #555;">kg/h</div>
                        <div style="font-size: 10px; color: #777; margin-top: 2px;">{perf['m_hp']:.5f} kg/s</div>
                    </div>
                """, unsafe_allow_html=True)

            # Volumes balayés
            st.markdown("""
                <div style="background: linear-gradient(135deg, #0f4c75 0%, #1b6ca8 100%);
                            padding: 6px 10px; border-radius: 8px; margin: 12px 0 8px 0;">
                    <span style="color: white; font-weight: bold; font-size: 12px;">📦 VOLUMES BALAYÉS</span>
                </div>
            """, unsafe_allow_html=True)

            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.markdown(f"""
                    <div style="background: #e3f2fd; border: 2px solid #1976d2; padding: 12px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; color: #1565c0; font-weight: bold;">📦 Vol. balayé BP</div>
                        <div style="font-size: 22px; color: #0d47a1; font-weight: bold;">{perf['v_bal_bp']:.3f}</div>
                        <div style="font-size: 11px; color: #555;">m³/h</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_v2:
                st.markdown(f"""
                    <div style="background: #ffebee; border: 2px solid #d32f2f; padding: 12px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; color: #c62828; font-weight: bold;">📦 Vol. balayé HP</div>
                        <div style="font-size: 22px; color: #b71c1c; font-weight: bold;">{perf['v_bal_hp']:.3f}</div>
                        <div style="font-size: 11px; color: #555;">m³/h</div>
                    </div>
                """, unsafe_allow_html=True)

            # Pression intermédiaire + taux de compression + ratio massique
            col_t0, col_t1, col_t2, col_t3 = st.columns(4)
            with col_t0:
                t_int_res = inter['t_int']
                p_int_res = inter['p_int']
                st.markdown(f"""
                    <div style="background: #e0f2f1; border-left: 4px solid #00897b; padding: 8px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 10px; color: #004d40; font-weight: bold;">🔀 pi</div>
                        <div style="font-size: 16px; color: #004d40; font-weight: bold;">{p_int_res:.3f} bar</div>
                        <div style="font-size: 13px; color: #00695c; font-weight: bold;">{t_int_res:.1f} °C</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_t1:
                tc_color = "#4caf50" if perf['tau_bp'] <= 6 else ("#ff9800" if perf['tau_bp'] <= 9 else "#f44336")
                st.markdown(f"""
                    <div style="background: #fafafa; border-left: 4px solid #607d8b; padding: 8px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 10px; color: #666; font-weight: bold;">τ BP (pi/p₀)</div>
                        <div style="font-size: 18px; color: {tc_color}; font-weight: bold;">{perf['tau_bp']:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_t2:
                th_color = "#4caf50" if perf['tau_hp'] <= 6 else ("#ff9800" if perf['tau_hp'] <= 9 else "#f44336")
                st.markdown(f"""
                    <div style="background: #fafafa; border-left: 4px solid #607d8b; padding: 8px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 10px; color: #666; font-weight: bold;">τ HP (pₖ/pi)</div>
                        <div style="font-size: 18px; color: {th_color}; font-weight: bold;">{perf['tau_hp']:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_t3:
                st.markdown(f"""
                    <div style="background: #e0f2f1; border-left: 4px solid #00897b; padding: 8px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 10px; color: #666; font-weight: bold;">r = ṁ_HP/ṁ_BP</div>
                        <div style="font-size: 18px; color: #004d40; font-weight: bold;">{perf['r']:.3f}</div>
                    </div>
                """, unsafe_allow_html=True)

            # Températures de refoulement
            col_tr1, col_tr2 = st.columns(2)
            with col_tr1:
                t2_val = pts['2']['T']
                t2_col = "#4caf50" if t2_val <= 100 else ("#ff9800" if t2_val <= 120 else "#f44336")
                st.markdown(f"""
                    <div style="background: #fafafa; border-left: 4px solid #1976d2; padding: 8px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 10px; color: #666; font-weight: bold;">🌡️ Refoul. BP (Point 2)</div>
                        <div style="font-size: 16px; color: {t2_col}; font-weight: bold;">{t2_val:.1f} °C</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_tr2:
                t4_val = pts['4']['T']
                t4_col = "#4caf50" if t4_val <= 100 else ("#ff9800" if t4_val <= 120 else "#f44336")
                st.markdown(f"""
                    <div style="background: #fafafa; border-left: 4px solid #d32f2f; padding: 8px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 10px; color: #666; font-weight: bold;">🌡️ Refoul. HP (Point 4)</div>
                        <div style="font-size: 16px; color: {t4_col}; font-weight: bold;">{t4_val:.1f} °C</div>
                    </div>
                """, unsafe_allow_html=True)

            # Titre vapeur bouteille
            x6_pct = perf['x6'] * 100
            st.markdown(f"""
                <div style="background: #e0f2f1; border-left: 4px solid #00897b; padding: 8px; border-radius: 4px; margin: 4px 0;">
                    <div style="font-size: 10px; color: #004d40; font-weight: bold;">
                        💧 Titre vapeur après 1er détendeur (x₆)
                    </div>
                    <div style="font-size: 16px; color: #004d40; font-weight: bold;">{x6_pct:.1f} %
                        <span style="font-size: 11px; color: #555;">— fraction de flash vers HP</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Pompe de circulation — dimensionnement
            if perf.get('has_pump'):
                st.markdown("""
                    <div style="background: linear-gradient(135deg, #4a235a 0%, #6c3483 100%);
                                padding: 6px 10px; border-radius: 8px; margin: 12px 0 8px 0;">
                        <span style="color: white; font-weight: bold; font-size: 12px;">🔧 DIMENSIONNEMENT POMPE</span>
                    </div>
                """, unsafe_allow_html=True)
                npsh_color = "#4caf50" if perf['npsh_ok'] else "#f44336"
                npsh_label = "✅ NPSH OK" if perf['npsh_ok'] else "⚠️ NPSH INSUFFISANT"
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.markdown(f"""
                        <div style="background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 8px; border-radius: 4px; margin: 4px 0;">
                            <div style="font-size: 10px; color: #666; font-weight: bold;">ṁ pompe</div>
                            <div style="font-size: 16px; color: #7b1fa2; font-weight: bold;">{perf['qm_pump']*3600:.2f} kg/h</div>
                            <div style="font-size: 11px; color: #777;">= {perf['pump_n']:.1f} × ṁ_BP</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"""
                        <div style="background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 8px; border-radius: 4px; margin: 4px 0;">
                            <div style="font-size: 10px; color: #666; font-weight: bold;">Débit volumique</div>
                            <div style="font-size: 16px; color: #7b1fa2; font-weight: bold;">{perf['qv_pump_m3h']:.3f} m³/h</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col_p2:
                    st.markdown(f"""
                        <div style="background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 8px; border-radius: 4px; margin: 4px 0;">
                            <div style="font-size: 10px; color: #666; font-weight: bold;">HMT</div>
                            <div style="font-size: 16px; color: #7b1fa2; font-weight: bold;">{perf['hmt_pump']:.1f} m</div>
                            <div style="font-size: 11px; color: #777;">ΔP = {perf['pump_dp']:.2f} bar | ρ = {perf['pump_rho']:.1f} kg/m³ (liq. sat. à p₀)</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"""
                        <div style="background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 8px; border-radius: 4px; margin: 4px 0;">
                            <div style="font-size: 10px; color: #666; font-weight: bold;">Puissance électrique pompe</div>
                            <div style="font-size: 16px; color: #7b1fa2; font-weight: bold;">{perf['w_pump']:.3f} kW</div>
                            <div style="font-size: 11px; color: #777;">η = {perf['pump_eta']*100:.0f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style="background: {'#e8f5e9' if perf['npsh_ok'] else '#ffebee'};
                                border-left: 4px solid {npsh_color}; padding: 8px; border-radius: 4px; margin: 4px 0;">
                        <div style="font-size: 13px; color: {npsh_color}; font-weight: bold;">{npsh_label}</div>
                        <div style="font-size: 11px; color: #555;">Hauteur colonne liquide : {perf['pump_height']:.1f} m
                        {'(minimum requis : 1,5 m)' if not perf['npsh_ok'] else '≥ 1,5 m — marge suffisante'}</div>
                    </div>
                """, unsafe_allow_html=True)

        with col_tab:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #37474f 0%, #263238 100%);
                            padding: 8px 12px; border-radius: 8px; margin-bottom: 10px;">
                    <span style="color: white; font-weight: bold; font-size: 13px;">📋 TABLEAU DES POINTS DU CYCLE</span>
                </div>
            """, unsafe_allow_html=True)

            tableau = []
            _mode_res = res.get('mode_original', res.get('mode', ''))
            _inj_partielle = (_mode_res == 'Injection partielle')
            labels = {
                '1':   'Point 1 — Aspiration BP',
                '2is': 'Point 2is — Compression BP (isentr.)',
                '2':   'Point 2 — Refoulement BP',
                '3':   'Point 3 — Aspiration HP (vap. sat. pi)',
                '4is': 'Point 4is — Compression HP (isentr.)',
                '4':   'Point 4 — Refoulement HP',
                '5':   'Point 5 — Sortie condenseur',
                '6':   'Point 6 — Sortie détendeur pi (diphasique)',
                '7':   'Point 7 — Entrée détendeur BP'       if _inj_partielle else 'Point 7 — Liquide saturé pi',
                '8':   'Point 8 — Sortie détendeur BP'       if _inj_partielle else 'Point 8 — Sortie détendeur BP (diphasique)',
                '9':   'Point 9 — Sortie évap. BP (avec surchauffe)' if _inj_partielle else None,
                '10':  'Point 10 — Sortie échangeur intermédiaire MP' if _inj_partielle else 'Point 10 — Sortie pompe MP (liquide refoulé)',
                '11':  None if _inj_partielle else 'Point 11 — Sortie évaporateur MP (vap. sat. pi)',
            }
            labels = {k: v for k, v in labels.items() if v is not None}
            for pt_key, pt_label in labels.items():
                pt = pts.get(pt_key, {})
                v_x = "---"
                if pt.get('V') is not None:
                    v_x = f"{pt['V']:.5f} m³/kg"
                elif pt.get('X') is not None:
                    v_x = f"X={pt['X']:.1f}%"
                tableau.append({
                    'Point': pt_label,
                    'T [°C]': f"{pt['T']:.2f}" if pt.get('T') is not None else "---",
                    'P [bar]': f"{pt['P']:.3f}" if pt.get('P') is not None else "---",
                    'h [kJ/kg]': f"{pt['H']:.2f}" if pt.get('H') is not None else "---",
                    's [kJ/kgK]': f"{pt['S']:.4f}" if pt.get('S') is not None else "---",
                    'v / X': v_x,
                })
            st.dataframe(tableau, use_container_width=True, hide_index=True)

            # Données intermédiaires + bilan massique
            _mode_res = res.get('mode', 'Injection totale')
            _titre_bilan = {'Injection totale': '🔀 Bouteille intermédiaire', 'Injection partielle': '💉 Injection partielle', 'Sous-refroidisseur (EVI)': '🔁 Sous-refroidisseur (EVI)'}.get(_mode_res, '🔀')
            st.markdown(f"""
                <div style="background: #e0f2f1; border: 1px solid #80cbc4; border-radius: 8px;
                            padding: 10px; margin-top: 10px; font-size: 12px;">
                    <div style="font-weight: bold; color: #004d40; margin-bottom: 6px;">
                        {_titre_bilan} — pi = {inter['p_int']:.3f} bar | ti = {inter['t_int']:.2f} °C
                    </div>
                    <div>h'_int = <b>{inter['h_liq']:.2f} kJ/kg</b> &nbsp;|&nbsp;
                         h''_int = <b>{inter['h_vap']:.2f} kJ/kg</b> &nbsp;|&nbsp;
                         r = ṁ_HP/ṁ_BP = <b>{perf['r']:.4f}</b></div>
                    <div style="margin-top:4px; color:#555;">{res.get('bilan_str','')}</div>
                </div>
            """, unsafe_allow_html=True)

            # Diagramme P-h
            st.markdown("""
                <div style="background: linear-gradient(135deg, #37474f 0%, #263238 100%);
                            padding: 6px 10px; border-radius: 8px; margin: 12px 0 6px 0;">
                    <span style="color: white; font-weight: bold; font-size: 12px;">📈 DIAGRAMME P-h</span>
                </div>
            """, unsafe_allow_html=True)
            _fluide_cp = obtenir_fluide_coolprop(res.get('fluide_affichage',
                             st.session_state.get('bi_fluide', FLUIDES[0])))
            _fig_ph = tracer_ph_bietage(res, _fluide_cp)
            if _fig_ph:
                st.pyplot(_fig_ph, use_container_width=True)
                plt.close(_fig_ph)

        # ── Bouton export PDF ─────────────────────────────────────────────────
        st.markdown("---")
        if st.button("📄 Exporter en PDF", key='btn_bi_pdf', use_container_width=False):
            try:
                # Récupérer le schéma avec labels
                _pdf_schema_img = None
                _cur_mode_pdf = res.get('mode_original', res.get('mode', ''))
                if _cur_mode_pdf == 'Injection totale':
                    _p = resource_path("schemaFluBiEtageInjTotalePompe1.png")
                    if os.path.exists(_p):
                        _pdf_schema_img = superposer_volumes_schema(_p, perf)
                elif _cur_mode_pdf == 'Injection totale avec bouteille BP':
                    _p = resource_path("schemaFluBiEtageInjTotalePompeEcHPlaque.png")
                    if os.path.exists(_p):
                        _pdf_schema_img = superposer_schema_bouteille_bp(_p, perf)
                elif _cur_mode_pdf == 'Injection partielle':
                    _p = resource_path("schemaFluInjPartielleEcgPlaque.png")
                    if os.path.exists(_p):
                        _pdf_schema_img = superposer_schema_inj_partielle(_p, perf)
                # Diagramme P-h (figure matplotlib)
                _fluide_cp_pdf = obtenir_fluide_coolprop(res.get('fluide_affichage', FLUIDES[0]))
                _fig_ph_pdf = tracer_ph_bietage(res, _fluide_cp_pdf)
                # Génération PDF
                _pdf_buf = generer_pdf_bietage(res, _fluide_cp_pdf, _pdf_schema_img, _fig_ph_pdf)
                if _fig_ph_pdf:
                    plt.close(_fig_ph_pdf)
                st.download_button(
                    label="⬇️ Télécharger le PDF",
                    data=_pdf_buf,
                    file_name=f"calcflu_bietage_{_cur_mode_pdf.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key='dl_bi_pdf'
                )
            except Exception as _e:
                st.error(f"Erreur génération PDF : {_e}")

    else:
        st.info("Renseignez les paramètres et cliquez sur **CALCULER** pour afficher les résultats.")

    # Note explicative
    with st.expander("ℹ️ Hypothèses des trois architectures"):
        st.markdown("""
        **Hypothèses communes**
        - Pression intermédiaire optimale : `pi = √(p₀ × pₖ)` (taux de compression égaux) — modifiable.
        - Compressions supposées **adiabatiques** avec rendements ηis_BP et ηis_HP.
        - Détentes **isenthalpiques**. Pertes de charge négligées.
        - `V_BP = ṁ_BP × v₁ / ηvol_BP` | `V_HP = ṁ_HP × v₃ / ηvol_HP`
        - `COP = Q_evap / (W_BP + W_HP + W_pompe)`

        ---
        **🔀 Injection totale** *(bouteille intermédiaire idéale)*
        > Toute la masse du condenseur passe par le détendeur 1 → bouteille à pi.
        > HP aspire la vapeur saturée (point 3 = h''_int). BP aspire le liquide saturé.
        > `r = (h₂ − h₇) / (h₃ − h₅)` avec `r = ṁ_HP / ṁ_BP`

        **💉 Injection partielle** *(désurchauffe du refoulement BP)*
        > Seule une fraction ṁ_inj est expansée à pi et injectée au refoulement BP.
        > Le reste ṁ_BP va directement à l'évaporateur (expansion simple h₅ → p₀).
        > `r = (h₂ − h₅) / (h₃ − h₅)` où h₃ = vapeur saturée à pi

        **🔁 Sous-refroidisseur / EVI** *(échangeur économiseur)*
        > Dérivation ṁ_bypass expansée à pi évapore dans l'échangeur et sous-refroidit le liquide principal.
        > HP aspire le mélange : refoulement BP + vapeur bypass à pi.
        > `β = (h₅ − h₅ₛᵤᵦ) / (h''_int − h₅)` | `r = 1 + β` | `h₃ = (h₂ + β·h''_int) / r`
        """)

elif onglet_selectionne == "Calculateur":
    # En-tête
    st.markdown("""
        <div style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                    padding: 10px 15px; border-radius: 10px; margin-bottom: 15px;">
            <span style="color: white; font-weight: bold; font-size: 15px;">🔬 CALCULATEUR DE PROPRIÉTÉS THERMODYNAMIQUES</span>
        </div>
    """, unsafe_allow_html=True)

    # Initialiser les variables de session pour le calculateur
    if 'calc_resultats' not in st.session_state:
        st.session_state.calc_resultats = None

    # Ligne 1 : Fluide et Type de calcul
    col_fluide, col_type = st.columns(2)

    with col_fluide:
        st.markdown("""
            <div style="background: #f1f5f9; border-left: 4px solid #6366f1; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
                <span style="font-weight: bold; color: #4338ca;">Fluide frigorigène</span>
            </div>
        """, unsafe_allow_html=True)
        fluide_calc = st.selectbox(
            "Sélectionner le fluide",
            FLUIDES,
            index=FLUIDES.index(st.session_state.fluide) if st.session_state.fluide in FLUIDES else 0,
            key='fluide_calculateur',
            label_visibility="collapsed"
        )

    with col_type:
        st.markdown("""
            <div style="background: #f1f5f9; border-left: 4px solid #6366f1; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
                <span style="font-weight: bold; color: #4338ca;">Type de calcul</span>
            </div>
        """, unsafe_allow_html=True)
        type_calcul = st.selectbox(
            "Sélectionner le type",
            ["Courbe de saturation", "Surchauffe / Deux phases"],
            key='type_calcul',
            label_visibility="collapsed"
        )

    # Section de saisie selon le type de calcul
    if type_calcul == "Courbe de saturation":
        st.markdown("""
            <div style="background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
                        padding: 8px 12px; border-radius: 8px; margin: 10px 0;">
                <span style="color: white; font-weight: bold; font-size: 13px;">📈 COURBE DE SATURATION</span>
            </div>
        """, unsafe_allow_html=True)

        # Type de courbe
        col_courbe, col_info = st.columns([1, 2])
        with col_courbe:
            type_courbe = st.selectbox(
                "Type de courbe",
                ["Courbe de bulle (Q=0)", "Courbe de rosée (Q=1)"],
                key='type_courbe_sat'
            )
        with col_info:
            st.markdown("""
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 10px; border-radius: 4px; margin-top: 25px;">
                    <span style="color: #92400e; font-weight: bold;">⚠️ Saisissez UNE seule valeur parmi les suivantes</span>
                </div>
            """, unsafe_allow_html=True)

        # Champs de saisie en 2 colonnes
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            temp_sat = st.number_input("Température [°C]", value=None, key='calc_temp_sat', format="%.2f")
            vol_sat = st.number_input("Volume massique [m³/kg]", value=None, key='calc_vol_sat', format="%.6f")
            entropie_sat = st.number_input("Entropie [kJ/(kg·K)]", value=None, key='calc_entropie_sat', format="%.4f")

        with col_s2:
            pression_sat = st.number_input("Pression [bar abs]", value=None, key='calc_pression_sat', format="%.3f")
            enthalpie_sat = st.number_input("Enthalpie [kJ/kg]", value=None, key='calc_enthalpie_sat', format="%.2f")
            titre_sat = st.number_input("Titre en vapeur X [0-1]", value=None, key='calc_titre_sat', format="%.3f", min_value=0.0, max_value=1.0)

        # Boutons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            btn_calc_sat = st.button("🔄 Calculer", type="primary", use_container_width=True, key='btn_calc_sat')
        with col_btn2:
            btn_eff_sat = st.button("🗑️ Effacer", use_container_width=True, key='btn_eff_sat')

        if btn_eff_sat:
            for key in ['calc_temp_sat', 'calc_pression_sat', 'calc_vol_sat', 'calc_enthalpie_sat', 'calc_entropie_sat', 'calc_titre_sat']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.calc_resultats = None
            st.rerun()

        if btn_calc_sat:
            try:
                fluide = obtenir_fluide_coolprop(fluide_calc)
                Q = 0.0 if "bulle" in type_courbe.lower() else 1.0

                # Compter les valeurs saisies
                valeurs = {
                    'T': temp_sat,
                    'P': pression_sat,
                    'v': vol_sat,
                    'h': enthalpie_sat,
                    's': entropie_sat,
                    'X': titre_sat
                }
                valeurs_saisies = {k: v for k, v in valeurs.items() if v is not None}

                if len(valeurs_saisies) == 0:
                    st.error("❌ Aucune valeur saisie")
                elif len(valeurs_saisies) > 1:
                    st.warning("⚠️ Saisissez une seule valeur pour la courbe de saturation")
                else:
                    code = list(valeurs_saisies.keys())[0]
                    val = valeurs_saisies[code]

                    if code == 'T':
                        T_k = val + 273.15
                        P_pa = PropsSI('P', 'T', T_k, 'Q', Q, fluide)
                    elif code == 'P':
                        P_pa = val * 1e5
                        T_k = PropsSI('T', 'P', P_pa, 'Q', Q, fluide)
                    elif code == 'h':
                        h_jkg = val * 1000
                        # Méthode itérative pour trouver T
                        T_low, T_high = 200, 400
                        for _ in range(50):
                            T_mid = (T_low + T_high) / 2
                            h_mid = PropsSI('H', 'T', T_mid, 'Q', Q, fluide)
                            if abs(h_mid - h_jkg) < 10:
                                break
                            if h_mid < h_jkg:
                                T_low = T_mid
                            else:
                                T_high = T_mid
                        T_k = T_mid
                        P_pa = PropsSI('P', 'T', T_k, 'Q', Q, fluide)
                    elif code == 's':
                        s_jkgk = val * 1000
                        T_low, T_high = 200, 400
                        for _ in range(50):
                            T_mid = (T_low + T_high) / 2
                            s_mid = PropsSI('S', 'T', T_mid, 'Q', Q, fluide)
                            if abs(s_mid - s_jkgk) < 1:
                                break
                            if s_mid < s_jkgk:
                                T_low = T_mid
                            else:
                                T_high = T_mid
                        T_k = T_mid
                        P_pa = PropsSI('P', 'T', T_k, 'Q', Q, fluide)
                    elif code == 'v':
                        T_low, T_high = 200, 400
                        for _ in range(50):
                            T_mid = (T_low + T_high) / 2
                            rho = PropsSI('D', 'T', T_mid, 'Q', Q, fluide)
                            v_mid = 1 / rho if rho > 0 else 0
                            if abs(v_mid - val) < 1e-8:
                                break
                            if v_mid < val:
                                T_low = T_mid
                            else:
                                T_high = T_mid
                        T_k = T_mid
                        P_pa = PropsSI('P', 'T', T_k, 'Q', Q, fluide)
                    elif code == 'X':
                        st.error("❌ X seul ne suffit pas, entrez T ou P")
                        st.stop()

                    # Calculer toutes les propriétés
                    T_c = T_k - 273.15
                    P_bar = P_pa / 1e5
                    h_kjkg = PropsSI('H', 'T', T_k, 'Q', Q, fluide) / 1000
                    s_kjkgk = PropsSI('S', 'T', T_k, 'Q', Q, fluide) / 1000
                    rho = PropsSI('D', 'T', T_k, 'Q', Q, fluide)
                    v_m3kg = 1 / rho if rho > 0 else 0

                    st.session_state.calc_resultats = {
                        'T': T_c, 'P': P_bar, 'v': v_m3kg, 'h': h_kjkg, 's': s_kjkgk, 'X': Q * 100
                    }
                    st.success("✅ Calcul effectué")

            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

    else:  # Surchauffe / Deux phases
        st.markdown("""
            <div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
                        padding: 8px 12px; border-radius: 8px; margin: 10px 0;">
                <span style="color: white; font-weight: bold; font-size: 13px;">🔥 SURCHAUFFE / DEUX PHASES</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 10px; border-radius: 4px; margin-bottom: 10px;">
                <span style="color: #92400e; font-weight: bold;">⚠️ Saisissez DEUX valeurs parmi les suivantes</span>
            </div>
        """, unsafe_allow_html=True)

        # Champs de saisie en 2 colonnes
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            temp_sur = st.number_input("Température [°C]", value=None, key='calc_temp_sur', format="%.2f")
            vol_sur = st.number_input("Volume massique [m³/kg]", value=None, key='calc_vol_sur', format="%.6f")
            entropie_sur = st.number_input("Entropie [kJ/(kg·K)]", value=None, key='calc_entropie_sur', format="%.4f")

        with col_s2:
            pression_sur = st.number_input("Pression [bar abs]", value=None, key='calc_pression_sur', format="%.3f")
            enthalpie_sur = st.number_input("Enthalpie [kJ/kg]", value=None, key='calc_enthalpie_sur', format="%.2f")
            titre_sur = st.number_input("Titre en vapeur X [0-1]", value=None, key='calc_titre_sur', format="%.3f", min_value=0.0, max_value=1.0)

        # Boutons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            btn_calc_sur = st.button("🔄 Calculer", type="primary", use_container_width=True, key='btn_calc_sur')
        with col_btn2:
            btn_eff_sur = st.button("🗑️ Effacer", use_container_width=True, key='btn_eff_sur')

        if btn_eff_sur:
            for key in ['calc_temp_sur', 'calc_pression_sur', 'calc_vol_sur', 'calc_enthalpie_sur', 'calc_entropie_sur', 'calc_titre_sur']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.calc_resultats = None
            st.rerun()

        if btn_calc_sur:
            try:
                fluide = obtenir_fluide_coolprop(fluide_calc)

                # Compter les valeurs saisies
                valeurs = {
                    'T': temp_sur,
                    'P': pression_sur,
                    'v': vol_sur,
                    'h': enthalpie_sur,
                    's': entropie_sur,
                    'X': titre_sur
                }
                valeurs_saisies = {k: v for k, v in valeurs.items() if v is not None}

                if len(valeurs_saisies) < 2:
                    st.error("❌ Saisissez au moins deux valeurs")
                elif len(valeurs_saisies) > 2:
                    st.warning("⚠️ Saisissez exactement deux valeurs")
                else:
                    codes = list(valeurs_saisies.keys())
                    vals = list(valeurs_saisies.values())

                    # Préparer les arguments pour PropsSI
                    args = []
                    for i, code in enumerate(codes):
                        val = vals[i]
                        if code == 'T':
                            args.extend(['T', val + 273.15])
                        elif code == 'P':
                            args.extend(['P', val * 1e5])
                        elif code == 'h':
                            args.extend(['H', val * 1000])
                        elif code == 's':
                            args.extend(['S', val * 1000])
                        elif code == 'v':
                            args.extend(['D', 1 / val if val > 0 else 1e10])
                        elif code == 'X':
                            args.extend(['Q', val])

                    # Calculer les propriétés
                    T_k = PropsSI('T', *args, fluide)
                    P_pa = PropsSI('P', *args, fluide)
                    h_jkg = PropsSI('H', *args, fluide)
                    s_jkgk = PropsSI('S', *args, fluide)
                    rho = PropsSI('D', *args, fluide)

                    try:
                        Q = PropsSI('Q', *args, fluide)
                        if Q < 0 or Q > 1:
                            Q = None
                    except:
                        Q = None

                    T_c = T_k - 273.15
                    P_bar = P_pa / 1e5
                    h_kjkg = h_jkg / 1000
                    s_kjkgk = s_jkgk / 1000
                    v_m3kg = 1 / rho if rho > 0 else 0

                    st.session_state.calc_resultats = {
                        'T': T_c, 'P': P_bar, 'v': v_m3kg, 'h': h_kjkg, 's': s_kjkgk,
                        'X': Q * 100 if Q is not None else None
                    }
                    st.success("✅ Calcul effectué")

            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

    # Section Résultats
    st.markdown("""
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    padding: 8px 12px; border-radius: 8px; margin: 15px 0 10px 0;">
            <span style="color: white; font-weight: bold; font-size: 13px;">📊 RÉSULTATS</span>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.calc_resultats:
        res = st.session_state.calc_resultats
        col_r1, col_r2 = st.columns(2)

        with col_r1:
            st.markdown(f'''
                <div style="background: #eff6ff; border: 2px solid #3b82f6; border-radius: 8px; padding: 12px; margin: 5px 0;">
                    <div style="font-size: 11px; color: #64748b; font-weight: bold;">🌡️ Température</div>
                    <div style="font-size: 20px; color: #1e40af; font-weight: bold;">{res['T']:.2f} °C</div>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown(f'''
                <div style="background: #eff6ff; border: 2px solid #3b82f6; border-radius: 8px; padding: 12px; margin: 5px 0;">
                    <div style="font-size: 11px; color: #64748b; font-weight: bold;">📦 Volume massique</div>
                    <div style="font-size: 20px; color: #1e40af; font-weight: bold;">{res['v']:.6f} m³/kg</div>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown(f'''
                <div style="background: #eff6ff; border: 2px solid #3b82f6; border-radius: 8px; padding: 12px; margin: 5px 0;">
                    <div style="font-size: 11px; color: #64748b; font-weight: bold;">🔄 Entropie</div>
                    <div style="font-size: 20px; color: #1e40af; font-weight: bold;">{res['s']:.4f} kJ/(kg·K)</div>
                </div>
            ''', unsafe_allow_html=True)

        with col_r2:
            st.markdown(f'''
                <div style="background: #eff6ff; border: 2px solid #3b82f6; border-radius: 8px; padding: 12px; margin: 5px 0;">
                    <div style="font-size: 11px; color: #64748b; font-weight: bold;">📊 Pression</div>
                    <div style="font-size: 20px; color: #1e40af; font-weight: bold;">{res['P']:.3f} bar</div>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown(f'''
                <div style="background: #eff6ff; border: 2px solid #3b82f6; border-radius: 8px; padding: 12px; margin: 5px 0;">
                    <div style="font-size: 11px; color: #64748b; font-weight: bold;">⚡ Enthalpie</div>
                    <div style="font-size: 20px; color: #1e40af; font-weight: bold;">{res['h']:.2f} kJ/kg</div>
                </div>
            ''', unsafe_allow_html=True)
            x_display = f"{res['X']:.1f} %" if res['X'] is not None else "N/A (surchauffe)"
            st.markdown(f'''
                <div style="background: #eff6ff; border: 2px solid #3b82f6; border-radius: 8px; padding: 12px; margin: 5px 0;">
                    <div style="font-size: 11px; color: #64748b; font-weight: bold;">💧 Titre en vapeur X</div>
                    <div style="font-size: 20px; color: #1e40af; font-weight: bold;">{x_display}</div>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("👆 Saisissez les valeurs et cliquez sur 'Calculer' pour afficher les résultats")

# Pied de page
st.markdown("""
    <div style="text-align: center; color: #64748b; padding: 1rem; margin-top: 3rem; border-top: 1px solid #e2e8f0;">
        <p><strong>Application développée par Christian Lucas</strong> | Bibliothèque CoolProp | L'utilisateur est responsable de la vérification des résultats</p>
    </div>
""", unsafe_allow_html=True)

# Note: Le rerun automatique a été supprimé car il causait des problèmes
# de navigation entre onglets. Streamlit gère les mises à jour automatiquement.
