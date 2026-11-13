# Monde VJ — Couche 19 : paysages et climats indépendants

**Version autonome HTML Windows / Chrome ou Edge.**

[Ouvrir le prototype](Monde_VJ_Atlas_3D_Couche_19_Climats_Independants.html) · [Journal technique](PROGRESS.md).

## Interface utilisateur

Choisir indépendamment un **paysage** et un **climat** ; bouton **🎲 Random Seed** (génère la seed sans lancer le monde), affichage et copie du numéro, puis **Générer le monde**. Le bouton de génération ne change jamais la seed. Les paramètres détaillés demeurent repliés dans **Paramètres avancés** et permettent la saisie manuelle d'une seed pour retrouver le monde.

Paysages : Mixte, Montagnes, Bord de mer, Plateaux, Collines, Vallées et lacs, Hautes montagnes (ancien profil enneigé renommé : le froid dépend maintenant du climat).

Climats : Tempéré, Aride, Tropical humide, Mousson, Froid / polaire, Sécheresse intense, Méditerranéen.

## Comportements physiques

À seed + paysage identiques, le relief 200×200 reste identique quelle que soit la météo choisie. Le climat règle : température initiale, ensoleillement/rayonnement, vent, fréquence/intensité des précipitations, évaporation, stocks d'eau initiaux, part d'eau souterraine héritée, recharge et graines.

L'humidité historique tropicale est financée par **transfert de l'eau de surface initiale** vers les nuages/vapeur, avec compensation d'énergie latente et gravitationnelle. Aucun apport d'eau artificiel pendant la simulation. Les masses d'eau initiales peuvent être différentes entre climats car elles représentent des histoires hydrologiques distinctes.

Les scénarios « Mousson » et « Méditerranéen » emploient une **oscillation stylisée de 20 jours simulés**, accélérée à titre expérimental : ce n'est pas une saisonnalité physique complète. La sécheresse intense est un scénario extrême prolongé, non un climat stable calibré. Le « bord de mer » reste un bassin fermé, sans marée.

## Échelle et garanties

2×2 km, 40 000 cellules de 10 m, 2 000 pas/jour. Le relief géomorphologique, les rivières, nappes phréatiques, les cinq sphères, la cryosphère et la pluie avec occlusion 3D sont conservés. La faune reste en pause.

**Vérifications :** les sept climats testés sur Montagnes + seed 42 pendant 160 pas, tous les bilans relatifs eau/énergie/matière sèche <1e-14, zéro erreur JS ; relief rigoureusement identique. Une journée complète (2 000 pas) validée sous Mixte + Tempéré avec masse 2,57e-15, énergie 6,64e-16, matière sèche 1,69e-16. Régression couche 18 : même profil tempéré, après 200 pas, égalité des tableaux de nuages, eau, vapeur, nappe et plantes et des bilans. WebGL2 SwiftShader validé 150 pas en polaire. Les 2 000 pas continus n'ont pas été validés sur **chacun** des autres profils, et le GPU matériel Windows doit encore être testé.
