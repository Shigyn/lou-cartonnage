# L'art du cartonnage par Lou : genere les pages SEO a partir de index.html (en-tete, pied et sections reutilises),
# plus sitemap.xml, robots.txt et 404.html.
# Usage : python -I pages-seo.py   (relancer apres toute modification de index.html)
import io, json, os, re

ICI = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://shigyn.github.io/lou-cartonnage/'
DOSSIER = '/lou-cartonnage/'    # chemin du site sur GitHub Pages (pour la page 404)
APERCU = True                   # False a la mise en ligne : robots.txt ouvert

# Ancres de l'accueil qui deviennent des pages dediees
MENU = {'#creations': 'creations/', '#savoir-faire': 'cartonnage/', '#commande': 'sur-commande/'}
# Ancres qui restent sur l'accueil (depuis une sous-page : ../#ancre)
ANCRES_ACCUEIL = ('#ou-trouver', '#contact')
ETIQUETTE = 'sur-titre'
CTA = '<a class="bouton bouton-plein" href="https://www.facebook.com/profile.php?id=737708401" target="_blank" rel="noopener">Écrire à Lou</a>'
BOUTON_404 = 'bouton bouton-plein'

FAQ_CREATIONS = [
    ('Les créations sont-elles des pièces uniques ?', 'Oui : chaque boîte et chaque carnet est assemblé et découpé à la main. Deux pièces d’un même modèle ne sont jamais tout à fait identiques.'),
    ('Où peut-on acheter les créations ?', 'En dépôt dans des boutiques d’artisans à Cambrai et à Paris, sur les marchés de Noël, ou directement auprès de Lou en lui écrivant.'),
    ('Comment entretenir une boîte en cartonnage ?', 'Gardez-la au sec et à l’abri du soleil direct. Un chiffon doux et sec suffit pour la dépoussiérer.'),
]
FAQ_CARTONNAGE = [
    ('Qu’est-ce que le cartonnage ?', 'C’est l’art de fabriquer des objets en carton rigide (boîtes, coffrets, carnets, cadres) puis de les habiller de papier, de toile ou de simili-cuir.'),
    ('Combien de temps faut-il pour une boîte ?', 'De quelques heures à plusieurs jours selon la taille et la finesse des découpes. La découpe des motifs est l’étape la plus longue.'),
    ('Le cartonnage est-il solide ?', 'Oui : le carton utilisé est épais et rigide, et les pièces sont renforcées. Une boîte bien faite se garde des années.'),
]
FAQ_COMMANDE = [
    ('Peut-on commander une boîte personnalisée ?', 'Oui : couleur, format, motif ou occasion, Lou crée sur commande. Écrivez-lui avec votre idée.'),
    ('Quel délai pour une commande ?', 'Il dépend de la pièce et de la période. Pour Noël ou un événement, pensez à commander quelques semaines à l’avance.'),
    ('Faites-vous des coffrets pour les mariages ou les naissances ?', 'Oui : coffrets souvenirs, boîtes à alliances, carnets d’invités ou marque-pages à offrir aux invités.'),
]

PAGES = [
    dict(chemin='creations/', titre='Boîtes, carnets et marque-pages en cartonnage faits main | L’art du cartonnage par Lou',
         description='Boîtes décoratives, coffrets, carnets, vide-poches, cadres et marque-pages en cartonnage, ornés de motifs découpés à la main. Pièces uniques, Hauts-de-France.',
         sur='Les créations', h1='Boîtes, carnets et marque-pages faits main',
         intro='Coffrets, boîtes à bijoux, carnets, vide-poches et cadres : chaque pièce est montée, habillée et découpée à la main. Des objets uniques, à garder ou à offrir.',
         blocs=[('section', 'creations', None)], faq=FAQ_CREATIONS, fil='Créations'),
    dict(chemin='cartonnage/', titre='Le cartonnage d’art, étape par étape | L’art du cartonnage par Lou',
         description='Qu’est-ce que le cartonnage ? Structure, habillage, découpe au scalpel et papier caché : découvrez comment Lou fabrique ses boîtes et ses carnets, pièce par pièce.',
         sur='Le savoir-faire', h1='Le cartonnage d’art, étape par étape',
         intro='Le cartonnage est un métier de patience : du carton brut à la boîte finie, chaque étape se fait à la main, jusqu’aux motifs découpés un à un.',
         blocs=[('section', 'savoir-faire', None), ('section', 'creations', None)], faq=FAQ_CARTONNAGE, fil='Le cartonnage'),
    dict(chemin='sur-commande/', titre='Coffret et boîte personnalisés sur commande | L’art du cartonnage par Lou',
         description='Coffret cadeau, boîte à bijoux ou à souvenirs, carnets et marque-pages personnalisés : Lou crée sur commande en cartonnage, pour une naissance, un mariage ou un anniversaire.',
         sur='Sur commande', h1='Coffrets et boîtes personnalisés sur commande',
         intro='Une couleur, un format, un motif ou une occasion particulière : Lou imagine avec vous une pièce en cartonnage rien qu’à vous.',
         blocs=[('section', 'commande', None), ('section', 'contact', None)], faq=FAQ_COMMANDE, fil='Sur commande'),
]

NL = '\n'

# ------------------------------------------------------------------ outils
def element(html, tag, ident):
    m = re.search(r'<%s\b[^>]*\bid="%s"[^>]*>' % (tag, re.escape(ident)), html)
    if not m:
        raise SystemExit('introuvable : %s#%s' % (tag, ident))
    pos, prof = m.end(), 1
    motif = re.compile(r'<(/?)%s\b' % tag)
    while prof:
        n = motif.search(html, pos)
        prof += -1 if n.group(1) else 1
        pos = n.end()
    return html[m.start():html.index('>', pos) + 1]

def pages_cibles():
    return set(v.split('#')[0] for v in MENU.values())

def reecrire_liens(bloc, prefixe):
    """Ancres devenues pages -> prefixe + page ; pages deja relatives -> prefixe + page ; ancres de l'accueil -> prefixe + ancre."""
    for ancre, page in MENU.items():
        bloc = bloc.replace('href="%s"' % ancre, 'href="%s%s"' % (prefixe, page))
    if prefixe:
        for page in pages_cibles():
            bloc = re.sub(r'href="(?!\.\./|https?:)%s' % re.escape(page), 'href="%s%s' % (prefixe, page), bloc)
        for ancre in ANCRES_ACCUEIL:
            bloc = bloc.replace('href="%s"' % ancre, 'href="%s%s"' % (prefixe, ancre))
        bloc = bloc.replace('href="#haut"', 'href="%s"' % prefixe)
    return bloc

def faq_html(faq):
    items = (NL + '      ').join('<details class="revele"><summary>%s</summary><p>%s</p></details>' % (q, a) for q, a in faq)
    return ('  <section class="faq">' + NL + '    <h2 class="faq-titre revele">Questions fréquentes</h2>' + NL
            + '    <div class="faq-liste">' + NL + '      ' + items + NL + '    </div>' + NL + '  </section>')

def jsonld(o):
    return '<script type="application/ld+json">%s</script>' % json.dumps(o, ensure_ascii=False)

def ecrire(chemin, texte):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    io.open(chemin, 'w', encoding='utf-8', newline='').write(texte)

# ------------------------------------------------------------------ accueil
src = io.open(os.path.join(ICI, 'index.html'), encoding='utf-8').read()
tete = src[src.index('<header class="tete"'):src.index('</header>') + 9]
accueil = src.replace(tete, reecrire_liens(tete, ''))
if 'rel="canonical"' not in accueil:
    accueil = accueil.replace('<meta name="description"', '<link rel="canonical" href="%s">' % SITE + NL + '<meta name="description"', 1)
ecrire(os.path.join(ICI, 'index.html'), accueil)
src = accueil

head = src[:src.index('</head>')]
head = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', head, flags=re.S)
head = re.sub(r'<link rel="canonical" href="[^"]*">\n?', '', head)
corps_debut = src[src.index('<body>'):src.index('<main id="haut">')]
corps_fin = src[src.index('</main>'):]

def entete_page(titre, description, canonical, prefixe_css):
    h = head
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % titre, h)
    h = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % description, h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % titre, h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % description, h)
    if canonical:
        h = h.replace('<meta name="description"', '<link rel="canonical" href="%s">' % canonical + NL + '<meta name="description"', 1)
    return re.sub(r'href="style\.css', 'href="%sstyle.css' % prefixe_css, h)

# ------------------------------------------------------------------ sous-pages
for p in PAGES:
    r = '../'
    h = entete_page(p['titre'], p['description'], SITE + p['chemin'], r)
    ld = [
        {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': p['fil'], 'item': SITE + p['chemin']}]},
        {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in p['faq']]},
    ]
    h += NL.join(jsonld(o) for o in ld) + NL

    debut = reecrire_liens(corps_debut, r)
    actuelle = 'href="%s%s"' % (r, p['chemin'])
    debut = debut.replace(actuelle, actuelle + ' aria-current="page"', 1)

    blocs = []
    for tag, ident, enveloppe in p['blocs']:
        b = element(src, tag, ident)
        b = ('  <section class="%s">' % enveloppe + NL + '    ' + b + NL + '  </section>') if enveloppe else '  ' + b
        blocs.append(reecrire_liens(b, r))

    entete = ('  <nav class="ariane" aria-label="Fil d’Ariane"><a href="%s">Accueil</a><span aria-current="page">%s</span></nav>' % (r, p['fil']) + NL
              + '  <header class="page-entete">' + NL
              + '    <p class="%s">%s</p>' % (ETIQUETTE, p['sur']) + NL
              + '    <h1>%s</h1>' % p['h1'] + NL
              + '    <p>%s</p>' % p['intro'] + NL
              + '    ' + CTA + NL + '  </header>')
    fin = corps_fin.replace('src="app.js', 'src="%sapp.js' % r)
    blocs = [b.replace('src="photos/', 'src="%sphotos/' % r) for b in blocs]
    html = (h + '</head>' + NL + debut + '<main id="haut">' + NL + entete + NL + NL
            + (NL + NL).join(blocs) + NL + NL + faq_html(p['faq']) + NL + fin)
    ecrire(os.path.join(ICI, p['chemin'], 'index.html'), html)

# ------------------------------------------------------------------ sitemap, robots, 404
urls = [SITE] + [SITE + p['chemin'] for p in PAGES]
ecrire(os.path.join(ICI, 'sitemap.xml'),
       '<?xml version="1.0" encoding="UTF-8"?>' + NL + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + NL
       + NL.join('  <url><loc>%s</loc></url>' % u for u in urls) + NL + '</urlset>' + NL)

robots = ('# Apercu : site cache aux moteurs. A la mise en ligne, mettre APERCU = False dans pages-seo.py.' + NL
          + 'User-agent: *' + NL + 'Disallow: /' + NL) if APERCU else ('User-agent: *' + NL + 'Allow: /' + NL)
ecrire(os.path.join(ICI, 'robots.txt'), robots + NL + 'Sitemap: %ssitemap.xml' % SITE + NL)

h404 = entete_page('Page introuvable | ' + re.search(r'<title>(.*?)</title>', head).group(1).split(' : ')[0],
                   'Cette page n’existe pas ou a changé d’adresse.', None, DOSSIER)
if '<meta name="robots"' not in h404:
    h404 = h404.replace('<title>', '<meta name="robots" content="noindex">' + NL + '<title>', 1)
debut404 = reecrire_liens(corps_debut, DOSSIER)
html404 = (h404 + '</head>' + NL + debut404 + '<main id="haut">' + NL
           + '  <header class="page-entete page-404">' + NL
           + '    <p class="%s">Erreur 404</p>' % ETIQUETTE + NL
           + '    <h1>Cette page n’existe pas</h1>' + NL
           + '    <p>Le lien est peut-être ancien, ou la page a changé d’adresse.</p>' + NL
           + '    <a class="%s" href="%s">Revenir à l’accueil</a>' % (BOUTON_404, DOSSIER) + NL
           + '  </header>' + NL + corps_fin.replace('src="app.js', 'src="%sapp.js' % DOSSIER))
ecrire(os.path.join(ICI, '404.html'), html404)
print('%d pages + accueil, sitemap.xml, robots.txt, 404.html' % len(PAGES))
