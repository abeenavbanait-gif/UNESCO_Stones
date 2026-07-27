import os
import sys
import re
import json
import ssl
import argparse
import time
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Attempt spaCy import
SPACY_AVAILABLE = False
nlp = None
try:
    import spacy
    try:
        # Disable parser and ner for extreme speedup during lemmatization
        nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        SPACY_AVAILABLE = True
        print("✅ spaCy ('en_core_web_sm') successfully loaded with fast pipeline.")
    except Exception as e:
        print(f"⚠️ spaCy model 'en_core_web_sm' loading error: {e}. Falling back to NLTK.")
except ImportError:
    print("⚠️ spaCy not found. Falling back to NLTK lemmatizer.")

# Fallback NLTK setup
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

nltk_lemmatizer = WordNetLemmatizer()

# Gemini LLM imports
GEMINI_LLM_AVAILABLE = False
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_LLM_AVAILABLE = True
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_LLM_AVAILABLE = True
    except ImportError:
        GEMINI_LLM_AVAILABLE = False

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  EXPANDED MEGA-DICTIONARY FOR GEOLOGICAL & ARCHITECTURAL MATERIALS          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ── 1. IGNEOUS ROCKS ──
igneous_rocks = [
    'granite', 'pink granite', 'grey granite', 'gray granite', 'black granite',
    'white granite', 'red granite', 'green granite', 'blue granite', 'brown granite',
    'golden granite', 'silver granite', 'rose granite', 'salmon granite',
    'rapakivi granite', 'orbicular granite', 'graphic granite', 'porphyritic granite',
    'alkali granite', 'peralkaline granite', 'two-mica granite', 'biotite granite',
    'muscovite granite', 'hornblende granite', 'garnet granite', 'tourmaline granite',
    'coarse-grained granite', 'fine-grained granite', 'medium-grained granite',
    'foliated granite', 'migmatitic granite', 'granitic',
    'diorite', 'quartz diorite', 'hornblende diorite', 'dioritic',
    'gabbro', 'olivine gabbro', 'norite', 'troctolite', 'anorthosite', 'gabbroic',
    'syenite', 'nepheline syenite', 'quartz syenite', 'alkali syenite', 'syenitic',
    'monzonite', 'quartz monzonite', 'monzodiorite', 'monzogabbro',
    'granodiorite', 'tonalite', 'trondhjemite', 'plagiogranite', 'granodioritic',
    'peridotite', 'dunite', 'harzburgite', 'lherzolite', 'wehrlite',
    'pyroxenite', 'hornblendite', 'websterite',
    'larvikite', 'essexite', 'theralite', 'ijolite', 'urtite',
    'aplite', 'pegmatite', 'granite pegmatite', 'pegmatitic',
    'diabase', 'dolerite', 'microgabbro', 'diabasic',
    'lamprophyre', 'minette', 'vogesite', 'kersantite', 'spessartite',
    'kimberlite', 'lamproite', 'carbonatite',
    'charnockite', 'enderbite', 'mangerite', 'adamellite', 'alaskite',
    'basalt', 'olivine basalt', 'alkali basalt', 'tholeiitic basalt',
    'flood basalt', 'columnar basalt', 'vesicular basalt', 'amygdaloidal basalt',
    'pillow basalt', 'basalt column', 'basaltic lava', 'basaltic',
    'andesite', 'hornblende andesite', 'pyroxene andesite', 'basaltic andesite', 'andesitic',
    'rhyolite', 'rhyolitic tuff', 'rhyolitic ignimbrite', 'rhyolitic',
    'dacite', 'quartz latite', 'dacitic',
    'obsidian', 'snowflake obsidian', 'mahogany obsidian', 'rainbow obsidian',
    'pumice', 'pumicite', 'reticulite', 'scoria', 'cinder', 'volcanic cinder', 'lapilli',
    'trachyte', 'quartz trachyte', 'alkali trachyte', 'trachytic',
    'phonolite', 'tephriphonolite', 'phonotephrite', 'tephrite', 'basanite',
    'nephelinite', 'leucitite', 'melilitite', 'latite', 'mugearite', 'hawaiite',
    'ignimbrite', 'welded tuff', 'ash-flow tuff', 'ignimbritic',
    'tuff', 'volcanic tuff', 'lithic tuff', 'crystal tuff', 'vitric tuff',
    'lapilli tuff', 'tuff breccia', 'hyaloclastite', 'tuffaceous',
    'tephra', 'volcanic ash', 'volcanic bomb', 'volcanic block', 'perlite', 'pitchstone',
    'agglomerate', 'volcanic agglomerate', 'tezontle', 'cantera', 'chiluca', 'recinto',
    'volcanic rock', 'volcanic stone', 'lava', 'lava stone', 'lava rock',
    'aa lava', 'pahoehoe', 'porphyry', 'feldspar porphyry', 'quartz porphyry',
    'imperial porphyry', 'green porphyry', 'red porphyry', 'porphyritic',
    'felsite', 'petrosilex', 'pietra lavica', 'basaltina',
    'trass', 'pozzolan', 'pozzolana', 'pozzolanic', 'peperino', 'sperone',
    'leucitite tuff', 'piperno',
]

# ── 2. SEDIMENTARY ROCKS ──
sedimentary_rocks = [
    'sandstone', 'red sandstone', 'yellow sandstone', 'brown sandstone',
    'white sandstone', 'grey sandstone', 'gray sandstone', 'pink sandstone',
    'green sandstone', 'buff sandstone', 'golden sandstone', 'dark sandstone',
    'quartz sandstone', 'arkose', 'arkosic sandstone', 'arkosic',
    'greywacke', 'graywacke', 'wacke', 'subgreywacke',
    'micaceous sandstone', 'ferruginous sandstone', 'calcareous sandstone',
    'glauconitic sandstone', 'feldspathic sandstone',
    'flagstone', 'flag stone', 'freestone', 'gritstone', 'grit', 'millstone grit', 'millstone',
    'arenite', 'quartz arenite', 'litharenite', 'arenaceous',
    'nubian sandstone', 'old red sandstone', 'new red sandstone',
    'bunter sandstone', 'keuper sandstone',
    'siltstone', 'silty sandstone', 'silty',
    'mudstone', 'mud stone', 'mud rock', 'claystone', 'clay stone',
    'shale', 'oil shale', 'black shale', 'calcareous shale', 'fissile shale',
    'slate-like shale', 'laminated shale', 'carbonaceous shale', 'shaly',
    'marl', 'marlstone', 'calcareous marl', 'argillaceous marl', 'marly',
    'conglomerate', 'puddingstone', 'polygenetic conglomerate',
    'monogenetic conglomerate', 'fanglomerate', 'conglomeratic',
    'breccia', 'fault breccia', 'sedimentary breccia', 'collapse breccia', 'brecciated',
    'tillite', 'diamictite', 'mixtite', 'loess', 'loessite', 'adobe',
    'turbidite', 'flysch', 'molasse', 'laterite', 'laterite stone', 'lateritic', 'plinthite',
    'bauxite', 'ironstone', 'bog iron', 'limonite', 'goethite',
    'ferricrete', 'calcrete', 'silcrete', 'duricrust',
    'limestone', 'oolitic limestone', 'oolite', 'ooid', 'oolitic',
    'fossiliferous limestone', 'shelly limestone', 'bioclastic limestone',
    'crinoidal limestone', 'nummulitic limestone', 'nummulite',
    'foraminiferal limestone', 'algal limestone', 'stromatolitic limestone',
    'reef limestone', 'coralline limestone', 'coral limestone',
    'micritic limestone', 'sparitic limestone', 'lithographic limestone',
    'chalk', 'chalky limestone', 'white chalk', 'grey chalk', 'chalky',
    'dolomite', 'dolostone', 'dolomitic limestone', 'magnesian limestone', 'dolomitic',
    'travertine', 'banded travertine', 'roman travertine', 'travertinic',
    'calcareous tufa', 'tufa', 'freshwater tufa', 'tufaceous',
    'calcarenite', 'calcilutite', 'calcisiltite', 'calcirudite',
    'coquina', 'lumachelle', 'lumachella',
    'coral stone', 'coral rock', 'coral rag', 'coralline',
    'ragstone', 'rag', 'kentish rag', 'clunch', 'clunch stone',
    'lias', 'blue lias', 'cornbrash', 'cornstone', 'caliche',
    'stalactite', 'stalagmite', 'flowstone', 'speleothem',
    'onyx marble', 'mexican onyx', 'egyptian onyx',
    'alabaster', 'gypsum alabaster', 'calcite alabaster',
    'gypsum', 'selenite', 'satin spar', 'desert rose', 'anhydrite',
    'chert', 'flint', 'hornstone', 'novaculite', 'cherty',
    'jasper', 'red jasper', 'yellow jasper', 'green jasper',
    'bloodstone', 'heliotrope', 'agate', 'banded agate', 'moss agate',
    'chalcedony', 'chrysoprase', 'carnelian', 'cornelian', 'sard',
    'onyx', 'sardonyx', 'opal', 'common opal', 'fire opal', 'precious opal',
    'diatomite', 'diatomaceous earth', 'tripolite', 'radiolarite',
    'phosphorite', 'evaporite', 'rock salt', 'halite',
    'coal', 'anthracite', 'lignite', 'peat', 'jet', 'amber',
]

# ── 3. METAMORPHIC ROCKS ──
metamorphic_rocks = [
    'slate', 'roofing slate', 'writing slate', 'black slate', 'grey slate',
    'gray slate', 'green slate', 'purple slate', 'red slate', 'blue slate',
    'welsh slate', 'vermont slate', 'slaty',
    'phyllite', 'sericite phyllite', 'phyllitic',
    'schist', 'mica schist', 'biotite schist', 'muscovite schist',
    'chlorite schist', 'talc schist', 'garnet schist', 'staurolite schist',
    'kyanite schist', 'sillimanite schist', 'hornblende schist',
    'actinolite schist', 'tremolite schist', 'glaucophane schist',
    'quartz-mica schist', 'calc-schist', 'schistose',
    'gneiss', 'granite gneiss', 'augen gneiss', 'banded gneiss',
    'biotite gneiss', 'hornblende gneiss', 'garnet gneiss',
    'paragneiss', 'orthogneiss', 'migmatitic gneiss', 'grey gneiss',
    'pink gneiss', 'leucogneiss', 'diorite gneiss', 'gneissic',
    'migmatite', 'diatexite', 'metatexite', 'migmatitic',
    'mylonite', 'protomylonite', 'ultramylonite', 'blastomylonite',
    'marble', 'white marble', 'black marble', 'grey marble', 'gray marble',
    'pink marble', 'red marble', 'green marble', 'yellow marble', 'blue marble',
    'cream marble', 'beige marble', 'brown marble', 'gold marble', 'rose marble',
    'veined marble', 'banded marble', 'brecciated marble', 'figured marble',
    'statuary marble', 'cipollino', 'cipolin', 'marbled', 'marbly',
    'dolomitic marble', 'calcitic marble', 'siliceous marble',
    'serpentine marble', 'ophicalcite', 'verde antico', 'breccia marble',
    'quartzite', 'white quartzite', 'pink quartzite', 'grey quartzite',
    'red quartzite', 'purple quartzite', 'ferruginous quartzite', 'itacolumite', 'quartzitic',
    'hornfels', 'spotted hornfels', 'pyroxene hornfels', 'andalusite hornfels',
    'cordierite hornfels', 'garnet hornfels',
    'granulite', 'felsic granulite', 'mafic granulite', 'charnockite granulite',
    'eclogite', 'amphibolite', 'garnet amphibolite', 'epidote amphibolite',
    'serpentinite', 'serpentine', 'serpentine stone', 'ophite',
    'verde antique', 'connemara marble',
    'soapstone', 'steatite', 'potstone', 'talc', 'talcose',
    'greenstone', 'green stone',
    'blueschist', 'blue schist', 'greenschist', 'green schist', 'whiteschist',
    'skarn', 'tactite', 'calc-silicate', 'cataclasite', 'lapis ollaris',
    'metaquartzite', 'metaconglomerate', 'metasandstone', 'metagraywacke',
    'metabasalt', 'metarhyolite', 'metagabbro', 'metadiorite',
    'metavolcanic', 'metasedimentary', 'greisen', 'rodingite', 'unakite', 'epidosite',
]

# ── 4. NAMED / TRADE / REGIONAL STONES ──
named_stones = [
    'carrara marble', 'bianco carrara', 'statuario', 'calacatta', 'arabescato',
    'bardiglio', 'botticino', 'rosso verona', 'rosso levanto', 'verde alpi',
    'pietra serena', 'pietra forte', 'pietra di firenze', 'pietra di lecce',
    'pietra leccese', 'carparo', 'trani stone', 'pietra d\'istria', 'istrian stone',
    'vicenza stone', 'nenfro', 'tufo romano', 'tufo napoletano', 'aurisina',
    'portoro', 'giallo siena', 'pietra piasentina', 'luserna stone',
    'marmo di candoglia', 'candoglia marble', 'travertino romano',
    'caen stone', 'pierre de caen', 'calcaire de caen', 'pierre de bourgogne',
    'burgundy stone', 'burgundy limestone', 'pierre de paris', 'lutetian limestone',
    'calcaire lutétien', 'pierre de volvic', 'volvic stone', 'volvic lava',
    'pierre de jaumont', 'pierre bleue', 'tournai stone', 'tuffeau', 'tuffeau blanc',
    'pierre de chassagne', 'pierre de massangis', 'marbre de sarrancolin',
    'portland stone', 'portland limestone', 'bath stone', 'bath limestone', 'bathstone',
    'cotswold stone', 'cotswold limestone', 'purbeck marble', 'purbeck stone',
    'kentish ragstone', 'kentish rag', 'barnack stone', 'clipsham stone',
    'beer stone', 'ham stone', 'ham hill stone', 'ancaster stone',
    'york stone', 'yorkshire stone', 'yorkshire sandstone', 'caithness flagstone',
    'aberdeen granite', 'cornish granite', 'dartmoor granite', 'pennant sandstone',
    'forest of dean stone', 'collyweston slate', 'stonesfield slate',
    'macael marble', 'blanco macael', 'montjuïc stone', 'montjuïc sandstone',
    'piedra de novelda', 'crema marfil', 'rojo alicante', 'negro marquina',
    'emperador marble', 'villamayor sandstone', 'piedra de salamanca',
    'lioz', 'lioz limestone', 'pedra lioz', 'pedra de ançã', 'ançã stone',
    'estremoz marble', 'moleanos stone',
    'pentelic marble', 'pentelikon marble', 'parian marble', 'paros marble',
    'proconnesian marble', 'marmara marble', 'hymettian marble', 'thasian marble',
    'cipollino marble', 'poros stone', 'piraeus limestone', 'afyon marble',
    'denizli travertine', 'cappadocia tuff', 'cappadocian tuff',
    'aswan granite', 'syene granite', 'red aswan granite', 'tura limestone',
    'tura stone', 'mokattam limestone', 'hathor alabaster', 'egyptian alabaster',
    'imperial porphyry', 'mons porphyrites', 'nubian sandstone', 'jerusalem stone',
    'meleke stone', 'jerusalem limestone', 'hebron stone', 'nari limestone',
    'mizzi ahmar', 'persepolis limestone', 'isfahan travertine',
    'makrana marble', 'makrana white', 'chunar sandstone', 'chunar stone',
    'agra red sandstone', 'fatehpur sikri sandstone', 'jodhpur sandstone',
    'jaisalmer stone', 'jaisalmer limestone', 'jaisalmer yellow', 'delhi quartzite',
    'khondalite', 'bhubaneswar stone', 'dholpur sandstone', 'bansi paharpur sandstone',
    'kota stone', 'kota limestone', 'kadappa stone', 'cuddapah stone',
    'udaipur green marble', 'dali marble', 'yunnan marble', 'fangshan marble',
    'shadow black', 'taihu stone', 'ōya stone', 'oya stone', 'oya tuff',
    'aji stone', 'aji granite', 'mikage stone', 'mikage granite',
    'indiana limestone', 'salem limestone', 'bedford limestone', 'georgia marble',
    'vermont marble', 'tennessee marble', 'crab orchard sandstone',
    'connecticut brownstone', 'pennsylvania bluestone', 'berea sandstone',
    'kasota stone', 'lyons sandstone', 'barre granite', 'cantera rosa',
    'oaxaca green stone', 'zimbabwean granite', 'zimbabwe black', 'nero impala',
]

# ── 5. DECORATIVE MINERALS & GEMSTONES ──
decorative_minerals = [
    'diamond', 'ruby', 'sapphire', 'emerald', 'lapis lazuli', 'lapis', 'lazurite',
    'malachite', 'azurite', 'turquoise', 'carnelian', 'cornelian', 'sard',
    'agate', 'banded agate', 'moss agate', 'fire agate', 'onyx', 'sardonyx',
    'chalcedony', 'chrysoprase', 'bloodstone', 'heliotrope', 'jasper', 'red jasper',
    'opal', 'garnet', 'amethyst', 'citrine', 'smoky quartz', 'rose quartz',
    'rock crystal', 'quartz crystal', 'topaz', 'tourmaline', 'peridot', 'olivine',
    'zircon', 'spinel', 'beryl', 'aquamarine', 'moonstone', 'labradorite', 'sunstone',
    'amazonite', 'feldspar', 'aventurine', 'tiger eye', 'obsidian', 'mother of pearl',
    'nacre', 'mother-of-pearl', 'coral', 'red coral', 'jet', 'whitby jet', 'amber',
    'baltic amber', 'jade', 'nephrite', 'jadeite', 'serpentine', 'bowenite',
    'rhodonite', 'sodalite', 'fluorite', 'fluorspar', 'blue john', 'hematite',
    'pyrite', 'fool\'s gold', 'pietra dura', 'pietre dure', 'parchin kari',
    'intarsia', 'scagliola', 'opus sectile', 'terrazzo',
]

# ── 6. CONSTRUCTION & MASONRY TERMS ──
construction_terms = [
    'ashlar', 'coursed ashlar', 'random ashlar', 'ashlar masonry',
    'rubble', 'coursed rubble', 'random rubble', 'uncoursed rubble', 'rubble masonry',
    'dressed stone', 'rough-hewn', 'rough hewn', 'rough-cut', 'rough cut',
    'cut stone', 'hewn stone', 'wrought stone', 'dimension stone', 'building stone',
    'natural stone', 'quarry stone', 'quarried stone', 'quarried', 'quarry', 'quarries',
    'freestone', 'brownstone', 'bluestone', 'greystone', 'whitestone', 'redstone',
    'paving stone', 'paver', 'sett', 'cobble', 'cobblestone', 'fieldstone',
    'capstone', 'coping stone', 'coping', 'cornerstone', 'quoin', 'quoin stone',
    'voussoir', 'keystone', 'springer', 'lintel', 'lintel stone',
    'threshold', 'threshold stone', 'sill', 'sill stone',
    'monolith', 'monolithic', 'megalith', 'megalithic', 'orthostat', 'menhir',
    'standing stone', 'stele', 'stela', 'stelae', 'obelisk', 'dry stone', 'drystone',
    'cyclopean', 'cyclopean masonry', 'polygonal masonry',
    'opus incertum', 'opus reticulatum', 'opus vittatum', 'opus caementicium',
    'opus testaceum', 'opus mixtum', 'opus quadratum', 'opus spicatum',
    'opus signinum', 'opus sectile', 'rustication', 'rusticated', 'bossage',
    'vermiculation', 'pointing', 'coursing', 'pier', 'pilaster',
    'engaged column', 'half-column', 'plinth', 'pedestal', 'socle', 'stylobate',
    'stereobate', 'crepidoma', 'dado', 'wainscot', 'baluster', 'balustrade',
    'parapet', 'battlement', 'crenellation', 'merlon', 'crenel', 'machicolation',
    'turret', 'bartisan', 'pinnacle', 'finial', 'gargoyle', 'tracery',
    'mullion', 'transom', 'tympanum', 'rose window', 'oculus', 'architrave',
    'entablature', 'cornice', 'frieze', 'capital', 'abacus', 'echinus', 'volute',
    'fluting', 'doric', 'ionic', 'corinthian', 'tuscan', 'composite', 'pediment',
    'stonemasonry', 'stone masonry', 'stonemason', 'stone mason',
    'stonecutter', 'stone cutter', 'stone carver', 'stone carving', 'masonry',
    'masoned', 'mason', 'blockwork', 'cladding', 'veneer', 'stone veneer',
    'facing', 'revetment', 'stone revetment', 'rock-cut', 'rock cut', 'rock-carved',
    'rock carved', 'rock architecture', 'cave temple', 'subterranean stone',
]

# ── 7. BUILDING MATERIALS (Non-stone) ──
building_materials = [
    'mortar', 'lime mortar', 'hydraulic lime', 'cement', 'portland cement',
    'concrete', 'reinforced concrete', 'roman concrete', 'plaster', 'lime plaster',
    'gypsum plaster', 'stucco', 'render', 'harling', 'roughcast', 'pebbledash',
    'brick', 'fired brick', 'sun-dried brick', 'mud brick', 'mud-brick', 'mudbrick',
    'glazed brick', 'roman brick', 'tile', 'roof tile', 'floor tile', 'wall tile',
    'glazed tile', 'terracotta', 'faience', 'zellige', 'azulejo', 'ceramic',
    'porcelain', 'stoneware', 'earthenware', 'adobe', 'rammed earth', 'pisé',
    'wattle and daub', 'cob', 'clay', 'mud wall', 'earth wall', 'timber',
    'timber frame', 'wood', 'wooden', 'oak', 'teak', 'mahogany', 'cedar', 'pine',
    'log', 'shingle', 'iron', 'wrought iron', 'cast iron', 'steel', 'bronze',
    'copper', 'lead', 'zinc', 'gold', 'silver', 'glass', 'stained glass',
    'mosaic', 'tessera', 'fresco', 'inlay', 'pietra dura', 'terrazzo',
]

# ── 8. ARCHITECTURAL ELEMENTS & STRUCTURES ──
architectural_elements = [
    'tomb', 'mosque', 'mausoleum', 'palace', 'fort', 'fortress', 'castle',
    'temple', 'cathedral', 'church', 'monastery', 'abbey', 'basilica',
    'shrine', 'sanctuary', 'stupa', 'pyramid', 'bridge', 'aqueduct',
    'amphitheatre', 'theatre', 'arena', 'bath', 'thermae', 'gate',
    'gateway', 'tower', 'pavilion', 'cenotaph', 'crypt', 'facade',
    'column', 'pillar', 'pier', 'arch', 'vault', 'dome', 'cupola',
    'spire', 'buttress', 'flying buttress', 'cornice', 'frieze',
    'pediment', 'capital', 'entablature', 'lintel', 'keystone',
    'voussoir', 'balustrade', 'parapet', 'crenellation', 'merlon',
    'machicolation', 'portcullis', 'drawbridge', 'moat', 'turret',
    'pinnacle', 'finial', 'gargoyle', 'tracery', 'rose window',
    'apse', 'nave', 'transept', 'chancel', 'altar', 'ambulatory',
    'clerestory', 'triforium', 'narthex', 'atrium', 'courtyard',
    'gallery', 'balcony', 'terrace', 'staircase', 'minbar',
    'mihrab', 'muqarnas', 'iwan', 'pishtaq', 'jali', 'portico',
    'peristyle', 'hypostyle', 'cella', 'pronaos', 'stylobate',
    'tympanum', 'architrave', 'corbel', 'bracket', 'cantilever',
    'roof', 'ceiling', 'floor', 'wall', 'foundation', 'plinth',
    'podium', 'base', 'shaft', 'pendentive', 'squinch', 'tambour',
    'drum', 'lantern', 'oculus', 'gable', 'cloister', 'minaret',
    'shikhara', 'vimana', 'gopura', 'mandapa', 'garbhagriha',
    'torana', 'pagoda', 'dagoba', 'chorten', 'candi',
]

# ── 9. EXCLUSION KEYWORDS ──
exclusion_keywords = [
    'cultural landscape', 'rock art', 'cave painting', 'cave art',
    'petroglyph', 'pictograph', 'geoglyph', 'vineyard', 'terrace farming',
    'rice terrace', 'agave landscape', 'coffee landscape', 'tea landscape',
    'fossil', 'hominid', 'hominin', 'paleontological', 'palaeontological',
    'oral tradition', 'intangible', 'prehistoric art', 'engravings',
    'textile', 'weaving', 'agricultural', 'pastoral', 'nomadic',
]

all_geological_stones = list(set(igneous_rocks + sedimentary_rocks + metamorphic_rocks))

_REGEX_CACHE = {}

def find_matches(lemmatized_text, keyword_list):
    """Find exact keyword matches using word boundaries."""
    matches = []
    for kw in keyword_list:
        kw_lower = kw.lower()
        if kw_lower not in _REGEX_CACHE:
            pattern = r'\b' + re.escape(kw_lower) + r'\b'
            _REGEX_CACHE[kw_lower] = re.compile(pattern, re.IGNORECASE)
        if _REGEX_CACHE[kw_lower].search(lemmatized_text):
            matches.append(kw)
    return list(set(matches))

def classify_geological(matched_stones):
    """Classify matched stone strings into Igneous, Sedimentary, or Metamorphic."""
    classes = set()
    for stone in matched_stones:
        sl = stone.lower()
        if sl in [s.lower() for s in igneous_rocks]:
            classes.add('Igneous')
        if sl in [s.lower() for s in sedimentary_rocks]:
            classes.add('Sedimentary')
        if sl in [s.lower() for s in metamorphic_rocks]:
            classes.add('Metamorphic')
    return classes

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  FAST BATCH LEMMATIZATION PIPELINE                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def batch_lemmatize(texts):
    """Batch lemmatize list of texts efficiently using spaCy pipe or NLTK."""
    results = []
    if SPACY_AVAILABLE and nlp is not None:
        print("⚡ Processing text batch via spaCy pipe...")
        docs = nlp.pipe(texts, batch_size=200)
        for doc in tqdm(docs, total=len(texts), desc="spaCy Lemmatization"):
            lemmas = [token.lemma_.lower() for token in doc if not token.is_punct]
            results.append(" ".join(lemmas))
    else:
        print("⚡ Processing text batch via NLTK...")
        for text in tqdm(texts, desc="NLTK Lemmatization"):
            words = word_tokenize(str(text).lower())
            lemmas = [nltk_lemmatizer.lemmatize(w) for w in words]
            results.append(" ".join(lemmas))
    return results

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CLASSIFICATION LOGIC FOR V2                                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def classify_site_row(row, lemmatized_text, site_name_lemmatized):
    site_name = str(row.get('site_name', '')).strip()
    criteria = str(row.get('criteria', '')).strip().lower()

    score = 0
    matched_categories = []
    matched_title_terms = []

    # ── LAYER 1: Criteria-based scoring ──
    if '(iv)' in criteria:
        score += 3
        matched_categories.append('Criterion_iv')
    if '(i)' in criteria:
        score += 2
        matched_categories.append('Criterion_i')
    if '(ii)' in criteria:
        score += 1
        matched_categories.append('Criterion_ii')

    # ── LAYER 2: Site Name & Title Keyword Analysis ──
    title_stone_keywords = [
        'stone', 'rock', 'quarry', 'quarries', 'monolith', 'megalith', 'stele',
        'stela', 'cave', 'carved', 'hewn', 'granite', 'marble', 'sandstone',
        'limestone', 'basalt', 'slate', 'tuff', 'travertine', 'dolomite',
        'masonry', 'ashlar', 'pyramid', 'cathedral', 'fortress', 'castle', 'aqueduct',
    ]
    for kw in title_stone_keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, site_name_lemmatized, re.IGNORECASE):
            score += 4
            matched_categories.append('Title_Stone_Keyword')
            matched_title_terms.append(kw)

    # ── LAYER 3: Stone & Mineral Matching ──
    geo_stone_matches = find_matches(lemmatized_text, all_geological_stones)
    if len(geo_stone_matches) >= 1:
        score += 4
        matched_categories.append('OUV_Stone')
    if len(geo_stone_matches) >= 3:
        score += 3
        matched_categories.append('OUV_Stone_3+')
    if len(geo_stone_matches) >= 5:
        score += 3
        matched_categories.append('OUV_Stone_5+')

    named_stone_matches = find_matches(lemmatized_text, named_stones)
    if len(named_stone_matches) >= 1:
        score += 5
        matched_categories.append('Named_Trade_Stone')
    if len(named_stone_matches) >= 3:
        score += 3
        matched_categories.append('Named_Trade_Stone_3+')

    deco_matches = find_matches(lemmatized_text, decorative_minerals)
    if len(deco_matches) >= 1:
        score += 2
        matched_categories.append('Decorative_Mineral')

    constr_matches = find_matches(lemmatized_text, construction_terms)
    if len(constr_matches) >= 2:
        score += 3
        matched_categories.append('OUV_Construction')
    if len(constr_matches) >= 5:
        score += 2
        matched_categories.append('OUV_Construction_5+')

    mat_matches = find_matches(lemmatized_text, building_materials)
    if len(mat_matches) >= 2:
        score += 2
        matched_categories.append('OUV_Materials')

    elem_matches = find_matches(lemmatized_text, architectural_elements)
    if len(elem_matches) >= 3:
        score += 3
        matched_categories.append('OUV_ArchElements')
    if len(elem_matches) >= 6:
        score += 2
        matched_categories.append('OUV_ArchElements_6+')

    # ── LAYER 4: Exclusion keyword check ──
    exclusion_hit = False
    for ex_kw in exclusion_keywords:
        if ex_kw in site_name.lower():
            exclusion_hit = True
            break
    if exclusion_hit:
        score = max(0, score - 3)

    all_stone_matches = list(set(geo_stone_matches + named_stone_matches))
    geo_classes = classify_geological(all_stone_matches)

    # Confidence tiering
    if score >= 10 or len(all_stone_matches) >= 2 or len(matched_title_terms) >= 1:
        confidence = 'HIGH'
    elif score >= 4 or len(all_stone_matches) >= 1 or len(constr_matches) >= 2:
        confidence = 'MEDIUM'
    elif score >= 1:
        confidence = 'LOW'
    else:
        confidence = 'NONE'

    return {
        'confidence_v2': confidence,
        'score_v2': score,
        'stone_count_v2': len(all_stone_matches),
        'stone_types_found_v2': '; '.join(sorted(all_stone_matches)),
        'stone_geological_class_v2': '; '.join(sorted(geo_classes)),
        'named_trade_stones_v2': '; '.join(sorted(named_stone_matches)),
        'decorative_minerals_v2': '; '.join(sorted(deco_matches)),
        'construction_terms_v2': '; '.join(sorted(constr_matches)),
        'architectural_elements_v2': '; '.join(sorted(elem_matches)),
        'matched_title_terms_v2': '; '.join(sorted(set(matched_title_terms))),
        'matched_categories_v2': '; '.join(matched_categories),
    }

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  GEMINI LLM INTEGRATION                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def evaluate_single_site(llm, idx, row, prompt_template):
    """Processes a single site with retry mechanism for robust LLM scan."""
    site_name = str(row.get('site_name', ''))
    brief_desc = str(row.get('brief_description', ''))[:1000]
    ouv_stmt = str(row.get('ouv_statement', ''))[:2000]
    prompt = prompt_template.format(site_name=site_name, brief_desc=brief_desc, ouv_stmt=ouv_stmt)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = llm.invoke(prompt)
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            res_json = json.loads(content)
            return {
                'index': idx,
                'has_geo': res_json.get("has_geological_material", False),
                'stone_types': "; ".join(res_json.get("stone_types", [])),
                'confidence': res_json.get("confidence", "NONE"),
                'summary': res_json.get("explanation", "")
            }
        except Exception as e:
            if attempt == max_retries - 1:
                return {
                    'index': idx,
                    'has_geo': False,
                    'stone_types': "",
                    'confidence': "ERROR",
                    'summary': str(e)
                }
            time.sleep(2 ** attempt)

def run_gemini_llm_rescan(df, gemini_api_key, concurrency=15):
    """Run Gemini 3.5 Flash LLM extraction on target candidate sites in parallel."""
    if not gemini_api_key or not GEMINI_LLM_AVAILABLE:
        print("ℹ️ Skipping Gemini LLM step (No API key provided or Gemini module unavailable).")
        df['llm_evaluated'] = False
        df['llm_has_geological_material'] = None
        df['llm_stone_types'] = None
        df['llm_confidence'] = None
        df['llm_summary'] = None
        return df

    print(f"🤖 Connecting to Gemini 3.5 Flash to evaluate candidate sites...")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.0
        )
    except Exception as e:
        print(f"⚠️ Error initializing Gemini 3.5 Flash: {e}")
        df['llm_evaluated'] = False
        return df

    # Target only borderline sites that have some building indicators (score_v2 >= 3) but do not have explicit stones matched by dictionary.
    # This filters out low-potential or blank landscapes, drastically reducing LLM calls while keeping accuracy high.
    target_indices = df[
        (df['confidence_v2'].isin(['MEDIUM', 'LOW'])) & 
        (df['stone_count_v2'] == 0) &
        (df['score_v2'] >= 3)
    ].index
    print(f"  Targeting {len(target_indices)} high-priority borderline sites for Gemini LLM evaluation...")

    results_map = {}
    
    prompt_template = (
        "You are an expert geologist and architectural historian.\n"
        "Analyze this UNESCO World Heritage Site information:\n"
        "Site Name: {site_name}\n"
        "Brief Description: {brief_desc}\n"
        "OUV Statement: {ouv_stmt}\n\n"
        "Question: Does this site feature or consist of natural building stone, rock-cut architecture, "
        "or specific geological materials (e.g. granite, limestone, sandstone, marble, slate, tuff, travertine, basalt, ashlar masonry)?\n"
        "Respond ONLY with a valid JSON object in this format:\n"
        "{{\n"
        '  "has_geological_material": true/false,\n'
        '  "stone_types": ["type1", "type2"],\n'
        '  "confidence": "HIGH"/"MEDIUM"/"LOW"/"NONE",\n'
        '  "explanation": "Short 1-sentence explanation"\n'
        "}}"
    )

    if len(target_indices) > 0:
        print(f"🚀 Running concurrency level {concurrency} for LLM evaluation...")
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {
                executor.submit(evaluate_single_site, llm, idx, df.loc[idx], prompt_template): idx
                for idx in target_indices
            }
            for future in tqdm(as_completed(futures), total=len(futures), desc="Gemini LLM Rescan"):
                res = future.result()
                results_map[res['index']] = res

    llm_has_geo = []
    llm_stones = []
    llm_conf = []
    llm_summary = []

    for idx in df.index:
        row = df.loc[idx]
        if idx in target_indices and idx in results_map:
            res = results_map[idx]
            llm_has_geo.append(res['has_geo'])
            llm_stones.append(res['stone_types'])
            llm_conf.append(res['confidence'])
            llm_summary.append(res['summary'])
        elif row['stone_count_v2'] > 0 or row['confidence_v2'] == 'HIGH':
            llm_has_geo.append(True)
            llm_stones.append(row['stone_types_found_v2'])
            llm_conf.append(row['confidence_v2'])
            llm_summary.append("Automatically verified by dictionary match")
        else:
            llm_has_geo.append(False)
            llm_stones.append("")
            llm_conf.append("SKIPPED")
            llm_summary.append("Not evaluated")

    df['llm_evaluated'] = True
    df['llm_has_geological_material'] = llm_has_geo
    df['llm_stone_types'] = llm_stones
    df['llm_confidence'] = llm_conf
    df['llm_summary'] = llm_summary
    return df

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  MAIN EXECUTION                                                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def main():
    parser = argparse.ArgumentParser(description="Rescan UNESCO No-Stone Sites for geological materials (v2).")
    parser.add_argument('--input', type=str, default='No_Stone_Sites-Table 1.csv', help='Input CSV file path')
    parser.add_argument('--output_dir', type=str, default='re-scan', help='Output directory name')
    parser.add_argument('--gemini_key', type=str, default=os.environ.get("GEMINI_API_KEY", ""), help='Gemini API Key')
    parser.add_argument('--concurrency', type=int, default=20, help='LLM API concurrency workers')
    args = parser.parse_args()

    input_file = args.input
    output_dir = args.output_dir
    gemini_key = args.gemini_key
    concurrency = args.concurrency

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    print(f"==========================================================")
    print(f"🏛️ UNESCO Heritage Sites - Geological Material Rescan v2 🏛️")
    print(f"==========================================================")
    print(f"Input file:  {input_file}")
    print(f"Output dir:  {output_dir}")
    print(f"NLP Engine:  {'spaCy (en_core_web_sm)' if SPACY_AVAILABLE else 'NLTK Lemmatizer'}")
    print(f"Gemini Key:  {'Provided' if gemini_key else 'Not provided'}")
    print(f"Concurrency: {concurrency}")
    print(f"----------------------------------------------------------")

    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} sites from {input_file}.\n")

    # Combine texts for fast batch lemmatization
    combined_texts = []
    site_name_texts = []
    for idx, row in df.iterrows():
        site_name = str(row.get('site_name', '')).strip()
        ouv = str(row.get('ouv_statement', '')).strip()
        brief_desc = str(row.get('brief_description', '')).strip() if 'brief_description' in row.index else ''
        combined_texts.append(f"{site_name}. {brief_desc} {ouv}")
        site_name_texts.append(site_name)

    # Fast batch lemmatization
    lemmatized_combined = batch_lemmatize(combined_texts)
    lemmatized_names = batch_lemmatize(site_name_texts)

    print("🔍 Executing upgraded multi-layer dictionary & spaCy title rescan...")
    v2_results_list = []
    for idx in range(len(df)):
        res = classify_site_row(df.iloc[idx], lemmatized_combined[idx], lemmatized_names[idx])
        v2_results_list.append(res)

    v2_df = pd.DataFrame(v2_results_list)
    df_rescanned = pd.concat([df, v2_df], axis=1)

    # Optional Gemini LLM step
    if gemini_key:
        df_rescanned = run_gemini_llm_rescan(df_rescanned, gemini_key, concurrency=concurrency)

    # Format URLs if unesco_id present
    if 'unesco_id' in df_rescanned.columns and 'unesco_url' not in df_rescanned.columns:
        df_rescanned['unesco_url'] = 'https://whc.unesco.org/en/list/' + df_rescanned['unesco_id'].astype(str)

    # Sort results by score
    df_rescanned = df_rescanned.sort_values('score_v2', ascending=False)

    # Save outputs into re-scan directory
    all_rescan_path = os.path.join(output_dir, 'rescanned_no_stone_sites.csv')
    built_rescan_path = os.path.join(output_dir, 'rescanned_built_geological_monuments.csv')

    df_rescanned.to_csv(all_rescan_path, index=False)
    
    # Filter built monuments (HIGH / MEDIUM confidence or stone_count_v2 > 0 or llm_has_geological_material == True)
    if 'llm_has_geological_material' in df_rescanned.columns:
        built_monuments = df_rescanned[
            (df_rescanned['confidence_v2'].isin(['HIGH', 'MEDIUM'])) |
            (df_rescanned['stone_count_v2'] > 0) |
            (df_rescanned['llm_has_geological_material'] == True)
        ]
    else:
        built_monuments = df_rescanned[
            (df_rescanned['confidence_v2'].isin(['HIGH', 'MEDIUM'])) |
            (df_rescanned['stone_count_v2'] > 0)
        ]
    built_monuments.to_csv(built_rescan_path, index=False)

    # Print summary report
    print(f"\n==========================================================")
    print(f"📊 RESCAN COMPLETE - SUMMARY RESULTS")
    print(f"==========================================================")
    print(f"Total Sites Rescanned:                     {len(df_rescanned)}")
    print(f"HIGH Confidence Sites (Newly Identified):   {len(df_rescanned[df_rescanned['confidence_v2']=='HIGH'])}")
    print(f"MEDIUM Confidence Sites:                   {len(df_rescanned[df_rescanned['confidence_v2']=='MEDIUM'])}")
    print(f"LOW Confidence Sites:                      {len(df_rescanned[df_rescanned['confidence_v2']=='LOW'])}")
    print(f"NONE (No stone/rock detected):             {len(df_rescanned[df_rescanned['confidence_v2']=='NONE'])}")
    print(f"----------------------------------------------------------")
    print(f"Total Rescanned Stone/Built Monument Sites: {len(built_monuments)}")
    print(f"All rescanned results saved to:             {all_rescan_path}")
    print(f"Rescanned built monuments saved to:         {built_rescan_path}")
    print(f"==========================================================\n")

    # Display sample top matches
    if len(built_monuments) > 0:
        print("🌟 Top Rescanned Sites with Identified Geological Material:")
        top_samples = built_monuments.head(15)
        for _, r in top_samples.iterrows():
            print(f"  • [{r['confidence_v2']}, Score {r['score_v2']}] {r['site_name']}")
            if str(r['stone_types_found_v2']).strip():
                print(f"    - Stones: {r['stone_types_found_v2']}")
            elif 'llm_stone_types' in r and str(r['llm_stone_types']).strip():
                print(f"    - LLM Stones: {r['llm_stone_types']}")
            if str(r['matched_title_terms_v2']).strip():
                print(f"    - Title terms: {r['matched_title_terms_v2']}")
            if str(r['construction_terms_v2']).strip():
                print(f"    - Construction terms: {r['construction_terms_v2'][:80]}")

if __name__ == '__main__':
    main()
