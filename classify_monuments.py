import pandas as pd
import re
import json
import ssl
import nltk
from tqdm import tqdm
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Bypass macOS SSL errors for NLTK downloads
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Ensure NLTK data is downloaded
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

lemmatizer = WordNetLemmatizer()

df = pd.read_csv('Imp Data/unesco_cultural_sites.csv')

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  LAYER 2: SITE NAME KEYWORDS (Architecture Categories)                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

name_keywords = {
    'Religious': [
        'temple', 'cathedral', 'mosque', 'church', 'monastery', 'abbey', 'basilica',
        'shrine', 'pagoda', 'stupa', 'chapel', 'synagogue', 'minaret', 'madrasa',
        'madrassa', 'medresa', 'medersa', 'convent', 'priory', 'hermitage', 'cloister',
        'sanctuary', 'wat', 'mandir', 'masjid', 'dargah', 'gurdwara', 'vihara',
        'chaitya', 'jinja', 'gopuram', 'torii', 'baptistery', 'oratory', 'mission',
        'candi', 'borobudur', 'angkor', 'sacred', 'holy', 'religious', 'pilgrimage',
        'papal', 'episcopal', 'monastic', 'friary', 'charterhouse', 'certosa',
        'duomo', 'minster', 'kirk', 'dom', 'munster'
    ],
    'Fortification': [
        'fort', 'fortress', 'citadel', 'castle', 'wall', 'tower', 'gate', 'rampart',
        'bastion', 'garrison', 'watchtower', 'blockhouse', 'barbican', 'keep',
        'donjon', 'alcazar', 'alcázar', 'kasbah', 'casbah', 'kremlin', 'fortification',
        'fortified', 'defensive', 'bulwark', 'stockade', 'battlement', 'redoubt',
        'enceinte', 'palisade', 'stronghold', 'acropolis', 'hillfort', 'oppidum',
        'ksar', 'ksour', 'ribat', 'presidio', 'castillo', 'zamok', 'burg',
        'festung', 'château fort', 'castelo', 'castello', 'qala', 'qalat', 'arg'
    ],
    'Palatial': [
        'palace', 'château', 'chateau', 'villa', 'manor', 'residence', 'royal',
        'schloss', 'palais', 'palazzo', 'estate', 'mansion', 'court', 'pavilion',
        'kiosk', 'serai', 'caravanserai', 'haveli', 'mahal', 'rajbari',
        'stately home', 'country house', 'summer palace', 'winter palace',
        'reggia', 'residenz', 'palacio', 'pazo', 'solar', 'hôtel'
    ],
    'Civic_Infrastructure': [
        'bridge', 'aqueduct', 'dam', 'canal', 'lighthouse', 'railway', 'town',
        'city', 'centre', 'center', 'civic', 'hall', 'theatre', 'theater',
        'opera', 'market', 'bazaar', 'square', 'plaza', 'piazza',
        'fountain', 'column', 'obelisk', 'arch', 'triumphal', 'monument',
        'memorial', 'statue', 'amphitheatre', 'amphitheater', 'colosseum',
        'arena', 'stadium', 'forum', 'baths', 'thermae', 'hospital',
        'university', 'library', 'observatory', 'warehouse', 'factory',
        'mill', 'mine', 'quarry', 'wharf', 'port', 'harbour', 'harbor',
        'dock', 'station', 'depot', 'clock tower', 'bell tower', 'belfry',
        'campanile', 'agora', 'stoa', 'odeon', 'hippodrome', 'circus',
        'capitol', 'guild', 'exchange', 'custom house', 'town hall',
        'rathaus', 'hôtel de ville', 'ayuntamiento', 'palazzo pubblico',
        'loggia', 'arcade', 'colonnade', 'portico'
    ],
    'Funerary': [
        'tomb', 'mausoleum', 'pyramid', 'necropolis', 'cemetery', 'burial',
        'grave', 'crypt', 'catacomb', 'tumulus', 'dolmen', 'megalith',
        'barrow', 'cairn', 'cenotaph', 'mortuary', 'funerary', 'sepulchre',
        'sepulcher', 'ossuary', 'charnel', 'mastaba', 'hypogeum', 'columbarium',
        'sarcophagus', 'kofun', 'kurgan', 'tholos'
    ],
    'Residential_Urban': [
        'house', 'dwelling', 'settlement', 'quarter', 'medina', 'old town',
        'historic centre', 'historic center', 'walled city', 'urban',
        'ghetto', 'caravansary', 'inn', 'hostel', 'hospice', 'almshouse',
        'tenement', 'farmstead', 'homestead', 'longhouse', 'pueblo',
        'trulli', 'sassi', 'historic district', 'colonial'
    ],
    'Industrial_Engineering': [
        'furnace', 'forge', 'ironworks', 'steelworks', 'workshop', 'kiln',
        'smelting', 'foundry', 'watermill', 'windmill', 'pumping station',
        'elevator', 'lift', 'crane', 'shipyard', 'dockyard', 'colliery',
        'mining', 'saltworks', 'salina', 'sugar mill', 'plantation',
        'textile mill', 'cotton mill', 'distillery', 'brewery', 'tannery'
    ],
    'Military': [
        'barracks', 'arsenal', 'armory', 'armoury', 'battery', 'bunker',
        'trench', 'military', 'naval', 'admiralty', 'war', 'defense',
        'defence', 'gunpowder', 'magazine', 'martello'
    ]
}

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  LAYER 3: STONE / ROCK / MINERAL MEGA-DICTIONARY                          ║
# ║  Organized by Geological Classification                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ─────────────────────────────────────────────────────────
# IGNEOUS ROCKS
# ─────────────────────────────────────────────────────────

igneous_rocks = [
    # ── Plutonic / Intrusive ──
    'granite', 'pink granite', 'grey granite', 'gray granite', 'black granite',
    'white granite', 'red granite', 'green granite', 'blue granite', 'brown granite',
    'golden granite', 'silver granite', 'rose granite', 'salmon granite',
    'rapakivi granite', 'orbicular granite', 'graphic granite', 'porphyritic granite',
    'alkali granite', 'peralkaline granite', 'two-mica granite', 'biotite granite',
    'muscovite granite', 'hornblende granite', 'garnet granite', 'tourmaline granite',
    'coarse-grained granite', 'fine-grained granite', 'medium-grained granite',
    'foliated granite', 'migmatitic granite',
    'diorite', 'quartz diorite', 'hornblende diorite',
    'gabbro', 'olivine gabbro', 'norite', 'troctolite', 'anorthosite',
    'syenite', 'nepheline syenite', 'quartz syenite', 'alkali syenite',
    'monzonite', 'quartz monzonite', 'monzodiorite', 'monzogabbro',
    'granodiorite', 'tonalite', 'trondhjemite', 'plagiogranite',
    'peridotite', 'dunite', 'harzburgite', 'lherzolite', 'wehrlite',
    'pyroxenite', 'hornblendite', 'websterite',
    'larvikite', 'essexite', 'theralite', 'ijolite', 'urtite',
    'aplite', 'pegmatite', 'granite pegmatite',
    'diabase', 'dolerite', 'microgabbro',
    'lamprophyre', 'minette', 'vogesite', 'kersantite', 'spessartite',
    'kimberlite', 'lamproite',
    'carbonatite',
    'charnockite', 'enderbite', 'mangerite',
    'adamellite', 'alaskite',

    # ── Volcanic / Extrusive ──
    'basalt', 'olivine basalt', 'alkali basalt', 'tholeiitic basalt',
    'flood basalt', 'columnar basalt', 'vesicular basalt', 'amygdaloidal basalt',
    'pillow basalt', 'basalt column', 'basaltic lava',
    'andesite', 'hornblende andesite', 'pyroxene andesite', 'basaltic andesite',
    'rhyolite', 'rhyolitic tuff', 'rhyolitic ignimbrite',
    'dacite', 'quartz latite',
    'obsidian', 'snowflake obsidian', 'mahogany obsidian', 'rainbow obsidian',
    'apache tear',
    'pumice', 'pumicite', 'reticulite',
    'scoria', 'cinder', 'volcanic cinder', 'lapilli',
    'trachyte', 'quartz trachyte', 'alkali trachyte',
    'phonolite', 'tephriphonolite', 'phonotephrite',
    'tephrite', 'basanite', 'nephelinite', 'leucitite', 'melilitite',
    'latite', 'mugearite', 'hawaiite', 'benmoreite',
    'comendite', 'pantellerite',
    'ignimbrite', 'welded tuff', 'ash-flow tuff',
    'tuff', 'volcanic tuff', 'lithic tuff', 'crystal tuff', 'vitric tuff',
    'lapilli tuff', 'tuff breccia', 'hyaloclastite',
    'tephra', 'volcanic ash', 'volcanic bomb', 'volcanic block',
    'perlite', 'pitchstone',
    'agglomerate', 'volcanic agglomerate',
    'tezontle', 'cantera', 'chiluca', 'recinto',
    'volcanic rock', 'volcanic stone', 'lava', 'lava stone', 'lava rock',
    'aa lava', 'pahoehoe',
    'porphyry', 'feldspar porphyry', 'quartz porphyry',
    'Imperial porphyry', 'green porphyry', 'red porphyry',
    'felsite', 'petrosilex',
    'pietra lavica', 'basaltina',
    'trass', 'pozzolan', 'pozzolana', 'pozzolanic',
    'peperino', 'sperone', 'leucitite tuff',
    'piperno',
]

# ─────────────────────────────────────────────────────────
# SEDIMENTARY ROCKS
# ─────────────────────────────────────────────────────────

sedimentary_rocks = [
    # ── Clastic / Detrital ──
    'sandstone', 'red sandstone', 'yellow sandstone', 'brown sandstone',
    'white sandstone', 'grey sandstone', 'gray sandstone', 'pink sandstone',
    'green sandstone', 'buff sandstone', 'golden sandstone',
    'quartz sandstone', 'arkose', 'arkosic sandstone',
    'greywacke', 'graywacke', 'wacke', 'subgreywacke',
    'micaceous sandstone', 'ferruginous sandstone', 'calcareous sandstone',
    'glauconitic sandstone', 'feldspathic sandstone',
    'flagstone', 'flag stone', 'freestone',
    'gritstone', 'grit', 'millstone grit', 'millstone',
    'arenite', 'quartz arenite', 'litharenite',
    'Nubian sandstone', 'Old Red Sandstone', 'New Red Sandstone',
    'Bunter sandstone', 'Keuper sandstone',
    'siltstone', 'silty sandstone',
    'mudstone', 'mud stone', 'mud rock', 'claystone', 'clay stone',
    'shale', 'oil shale', 'black shale', 'calcareous shale', 'fissile shale',
    'slate-like shale', 'laminated shale', 'carbonaceous shale',
    'marl', 'marlstone', 'calcareous marl', 'argillaceous marl',
    'conglomerate', 'puddingstone', 'polygenetic conglomerate',
    'monogenetic conglomerate', 'fanglomerate',
    'breccia', 'fault breccia', 'sedimentary breccia', 'collapse breccia',
    'intraformational breccia',
    'tillite', 'diamictite', 'mixtite',
    'loess', 'loessite', 'adobe',
    'turbidite', 'flysch', 'molasse',
    'laterite', 'laterite stone', 'lateritic', 'plinthite',
    'bauxite',
    'ironstone', 'bog iron', 'limonite', 'goethite',
    'ferricrete', 'calcrete', 'silcrete', 'duricrust',

    # ── Chemical / Precipitate ──
    'limestone', 'oolitic limestone', 'oolite', 'ooid',
    'fossiliferous limestone', 'shelly limestone', 'bioclastic limestone',
    'crinoidal limestone', 'nummulitic limestone', 'nummulite',
    'foraminiferal limestone', 'algal limestone', 'stromatolitic limestone',
    'reef limestone', 'coralline limestone', 'coral limestone',
    'micritic limestone', 'sparitic limestone',
    'lithographic limestone',
    'chalk', 'chalky limestone', 'white chalk', 'grey chalk',
    'dolomite', 'dolostone', 'dolomitic limestone', 'magnesian limestone',
    'travertine', 'banded travertine', 'Roman travertine',
    'calcareous tufa', 'tufa', 'freshwater tufa',
    'calcarenite', 'calcilutite', 'calcisiltite', 'calcirudite',
    'coquina', 'lumachelle', 'lumachella',
    'coral stone', 'coral rock', 'coral rag', 'coralline',
    'ragstone', 'rag', 'Kentish rag',
    'clunch', 'clunch stone',
    'lias', 'blue lias',
    'cornbrash', 'cornstone',
    'caliche',
    'stalactite', 'stalagmite', 'flowstone', 'speleothem',
    'onyx marble', 'Mexican onyx', 'Egyptian onyx',
    'alabaster', 'gypsum alabaster', 'calcite alabaster',
    'gypsum', 'selenite', 'satin spar', 'desert rose',
    'anhydrite',
    'chert', 'flint', 'hornstone', 'novaculite',
    'jasper', 'red jasper', 'yellow jasper', 'green jasper',
    'bloodstone', 'heliotrope',
    'agate', 'banded agate', 'moss agate', 'fire agate', 'blue lace agate',
    'chalcedony', 'chrysoprase', 'carnelian', 'cornelian', 'sard',
    'onyx', 'sardonyx',
    'opal', 'common opal', 'fire opal', 'precious opal',
    'diatomite', 'diatomaceous earth', 'tripolite',
    'radiolarite',
    'phosphorite', 'apatite rock',
    'evaporite', 'rock salt', 'halite', 'potash',
    'coal', 'anthracite', 'bituminous', 'lignite', 'peat',
    'jet',
    'amber',

    # ── Special sedimentary types ──
    'nodular limestone', 'massive limestone', 'bedded limestone',
    'flaggy limestone', 'rubbly limestone', 'marly limestone',
    'earthy limestone', 'crystalline limestone',
    'pisolite', 'pisolitic limestone',
    'boundstone', 'grainstone', 'packstone', 'wackestone', 'mudstone limestone',
    'rudstone', 'floatstone',
]

# ─────────────────────────────────────────────────────────
# METAMORPHIC ROCKS
# ─────────────────────────────────────────────────────────

metamorphic_rocks = [
    # ── Foliated ──
    'slate', 'roofing slate', 'writing slate', 'black slate', 'grey slate',
    'gray slate', 'green slate', 'purple slate', 'red slate', 'blue slate',
    'Welsh slate', 'Vermont slate', 'Vallorbe slate',
    'phyllite', 'sericite phyllite',
    'schist', 'mica schist', 'biotite schist', 'muscovite schist',
    'chlorite schist', 'talc schist', 'garnet schist', 'staurolite schist',
    'kyanite schist', 'sillimanite schist', 'hornblende schist',
    'actinolite schist', 'tremolite schist', 'glaucophane schist',
    'quartz-mica schist', 'calc-schist',
    'gneiss', 'granite gneiss', 'augen gneiss', 'banded gneiss',
    'biotite gneiss', 'hornblende gneiss', 'garnet gneiss',
    'paragneiss', 'orthogneiss', 'migmatitic gneiss', 'grey gneiss',
    'pink gneiss', 'leucogneiss', 'diorite gneiss',
    'migmatite', 'diatexite', 'metatexite',
    'mylonite', 'protomylonite', 'ultramylonite', 'blastomylonite',

    # ── Non-Foliated ──
    'marble', 'white marble', 'black marble', 'grey marble', 'gray marble',
    'pink marble', 'red marble', 'green marble', 'yellow marble', 'blue marble',
    'cream marble', 'beige marble', 'brown marble', 'gold marble', 'rose marble',
    'veined marble', 'banded marble', 'brecciated marble', 'figured marble',
    'statuary marble', 'cipollino', 'cipolin',
    'dolomitic marble', 'calcitic marble', 'siliceous marble',
    'serpentine marble', 'ophicalcite', 'verde antico',
    'breccia marble', 'onyx marble',
    'quartzite', 'white quartzite', 'pink quartzite', 'grey quartzite',
    'red quartzite', 'purple quartzite', 'ferruginous quartzite', 'itacolumite',
    'hornfels', 'spotted hornfels', 'pyroxene hornfels', 'andalusite hornfels',
    'cordierite hornfels', 'garnet hornfels',
    'granulite', 'felsic granulite', 'mafic granulite', 'charnockite granulite',
    'eclogite',
    'amphibolite', 'garnet amphibolite', 'epidote amphibolite',
    'serpentinite', 'serpentine', 'serpentine stone', 'ophite',
    'verde antique', 'verde antico', 'Connemara marble',
    'soapstone', 'steatite', 'potstone', 'talc', 'talcose',
    'greenstone', 'green stone',
    'blueschist', 'blue schist', 'greenschist', 'green schist',
    'whiteschist',
    'skarn', 'tactite', 'calc-silicate',
    'cataclasite',
    'lapis ollaris',
    'novaculite',
    'metaquartzite', 'metaconglomerate', 'metasandstone', 'metagraywacke',
    'metabasalt', 'metarhyolite', 'metagabbro', 'metadiorite',
    'metavolcanic', 'metasedimentary',
    'greisen',
    'rodingite',
    'unakite',
    'epidosite',
]

# ─────────────────────────────────────────────────────────
# FAMOUS NAMED / TRADE / LOCAL STONES (By Country/Region)
# ─────────────────────────────────────────────────────────

named_stones = {
    'Italian': [
        'Carrara marble', 'Bianco Carrara', 'Statuario', 'Calacatta', 'Arabescato',
        'Bardiglio', 'Venato', 'Bianco Venato', 'Bianco Statuario',
        'Botticino', 'Botticino classico', 'Botticino fiorito',
        'Rosso Verona', 'Rosso Levanto', 'Rosso Ammonitico', 'Rosso Asiago',
        'Verde Alpi', 'Verde Guatemala', 'Verde Issorie', 'Verde Acceglio',
        'pietra serena', 'pietra forte', 'pietra di Firenze',
        'pietra di Lecce', 'pietra leccese', 'carparo',
        'Trani stone', 'pietra di Trani', 'Apricena stone',
        'pietra d\'Istria', 'Istrian stone',
        'Vicenza stone', 'pietra di Vicenza', 'Nanto stone',
        'Pietra di Finale', 'Finale stone',
        'nenfro', 'tufo', 'tufo romano', 'tufo napoletano', 'tufo giallo',
        'panchina', 'panchina livornese',
        'Aurisina', 'Aurisina fiorita', 'Aurisina chiara', 'Aurisina granitello',
        'Chiampo', 'pietra di Chiampo',
        'Lessinia stone', 'pietra della Lessinia',
        'Breccia Aurora', 'Breccia Oniciata', 'Breccia Pernice',
        'Portoro', 'Porto venere marble', 'nero Portoro',
        'Giallo Siena', 'Giallo Reale', 'Giallo Antico',
        'Rosa Portogallo', 'Rosa Perlino', 'Rosa Asiago', 'Rosa Corallo',
        'Breccia di Seravezza', 'Breccia Medicea', 'Breccia Stazzema',
        'Fior di Pesco', 'Paonazzo', 'Paonazzetto',
        'pietra di Angera', 'pietra di Sarnico', 'pietra di Credaro',
        'pietra piasentina', 'pietra di Luserna', 'luserna stone',
        'Beola', 'beola ghiandonata', 'Serizzo', 'serizzo antigorio',
        'pietra di Comiso', 'Ragusa stone', 'Modica stone',
        'pietra lavica', 'Etna lava stone', 'basaltina',
        'travertino romano', 'travertino di Tivoli', 'travertino classico',
        'Nero Marquina', 'Nero Assoluto',
        'Bianco Sivec', 'Bianco Lasa', 'Lasa marble',
        'Pietra di Saltrio', 'Pietra Dorata', 'Pietra Serena del Firenzuola',
        'Candoglia marble', 'marmo di Candoglia',
        'Crema Valencia', 'Crema Marfil',
    ],
    'French': [
        'Caen stone', 'Pierre de Caen', 'calcaire de Caen',
        'Pierre de Bourgogne', 'Burgundy stone', 'Burgundy limestone',
        'Pierre de Paris', 'Lutetian limestone', 'calcaire lutétien',
        'Pierre de Lens', 'Pierre de Fontvieille',
        'Pierre de Volvic', 'Volvic stone', 'Volvic lava',
        'Pierre de Jaumont', 'Jaumont stone',
        'pierre bleue', 'Belgian blue stone', 'Tournai stone', 'Tournai marble',
        'Pierre de Euville', 'Pierre de Savonnières',
        'Pierre de Comblanchien', 'Comblanchien stone',
        'tuffeau', 'tuffeau blanc', 'tuffeau jaune',
        'Pierre de Richemont', 'Pierre de Crazannes', 'Pierre de Chauvigny',
        'Pierre de Vilhonneur', 'Pierre de Sireuil',
        'Pierre de Angoulême', 'Pierre de Hauterive',
        'Pierre de Saint-Maximin', 'Pierre de Conflans',
        'Pierre du Lot', 'Pierre du Périgord',
        'grès des Vosges', 'grès rose', 'Vosges sandstone',
        'Pierre de Berchères', 'Pierre de Chartres',
        'Pierre de Tonnerre', 'Pierre de Meuse',
        'marbre de Carrières-Saint-Denis',
        'Echaillon stone', 'Pierre d\'Echaillon',
        'Chassagne stone', 'Pierre de Chassagne',
        'Massangis stone', 'Pierre de Massangis',
        'Rocheret stone', 'Pierre de Rocheret',
        'Lavoux stone', 'Pierre de Lavoux',
        'Estaillades stone', 'Pierre des Estaillades',
        'Vers stone', 'Pierre de Vers',
        'Brauvilliers stone',
        'marbre campan', 'campan marble', 'marbre de campan',
        'Languedoc marble', 'marbre du Languedoc',
        'Griotte marble', 'marbre griotte',
        'Sarrancolin marble', 'marbre de Sarrancolin',
    ],
    'English_UK': [
        'Portland stone', 'Portland limestone', 'Portland Whitbed', 'Portland Basebed',
        'Bath stone', 'Bath limestone', 'Bathstone',
        'Cotswold stone', 'Cotswold limestone',
        'Guiting stone', 'Taynton stone', 'Burford stone',
        'Purbeck marble', 'Purbeck stone', 'Purbeck limestone',
        'Kentish ragstone', 'Kentish rag', 'ragstone',
        'Barnack stone', 'Barnack rag',
        'Chilmark stone', 'Tisbury stone',
        'Clipsham stone', 'Clipsham limestone',
        'Beer stone', 'Beer limestone',
        'Ham stone', 'Ham Hill stone', 'Hamstone',
        'Ancaster stone', 'Ancaster limestone',
        'Headington stone', 'Headington freestone',
        'Reigate stone', 'Reigate firestone',
        'York stone', 'Yorkshire stone', 'Yorkshire sandstone',
        'Caithness stone', 'Caithness flagstone',
        'Corsehill sandstone', 'Locharbriggs sandstone',
        'Aberdeen granite', 'Rubislaw granite',
        'Cornish granite', 'Dartmoor granite', 'Bodmin granite',
        'Mountsorrel granite', 'Shap granite',
        'Peterhead granite', 'De Lank granite', 'Penryn granite',
        'Kemnay granite',
        'Blue Pennant sandstone', 'Pennant sandstone', 'Pennant stone',
        'Forest of Dean stone', 'Forest stone',
        'Grinshill sandstone', 'Grinshill stone',
        'Hollington stone', 'Hollington sandstone',
        'Combe Down stone', 'Combe Down limestone',
        'Doulting stone', 'Doulting limestone',
        'Mansfield stone', 'Mansfield sandstone',
        'Stanton Moor stone', 'Stancliffe stone',
        'Darley Dale stone', 'Darley Dale sandstone',
        'Woodkirk stone', 'Bramley Fall stone',
        'Blaxter stone', 'Catcastle stone', 'Dunhouse stone',
        'Dundee sandstone', 'Craigleith sandstone',
        'Edinburgh stone', 'Hailes stone',
        'Caen stone',
        'Weldon stone',
        'Ketton stone', 'Ketton limestone',
        'Collyweston slate', 'Stonesfield slate',
    ],
    'Spanish_Portuguese': [
        'Macael marble', 'blanco Macael', 'gris Macael',
        'Montjuïc stone', 'Montjuïc sandstone', 'piedra de Montjuïc',
        'piedra de Novelda', 'piedra de Colmenar',
        'piedra caliza de Úbeda', 'piedra de Úbeda',
        'Calatorao alabaster', 'alabastro de Calatorao',
        'Bateig stone', 'piedra Bateig',
        'Piedra Rosa Sepúlveda', 'Rosa Sepúlveda',
        'Crema Marfil', 'Crema Marfil marble',
        'Rojo Alicante', 'Rojo Alicante marble',
        'Negro Marquina', 'Marquina marble',
        'Emperador', 'Emperador marble', 'Emperador Dark', 'Emperador Light',
        'Villamayor sandstone', 'piedra de Villamayor', 'piedra de Salamanca',
        'piedra franca', 'piedra de Molineros',
        'piedra arenisca', 'piedra caliza',
        'cantería', 'sillar', 'sillería', 'sillarejo', 'mampostería',
        'Lioz', 'Lioz limestone', 'pedra lioz', 'calcário lioz',
        'pedra de Ançã', 'Ançã stone', 'calcário de Ançã',
        'Estremoz marble', 'mármore de Estremoz',
        'Moleanos stone', 'pedra de Moleanos',
        'Vidraço stone',
        'Alpinina stone',
        'Semi-Rijo stone',
    ],
    'Greek_Turkish': [
        'Pentelic marble', 'Pentelikon marble', 'Pentelicus marble',
        'Parian marble', 'lychnites', 'Paros marble',
        'Proconnesian marble', 'Proconnesus marble', 'Marmara marble',
        'Hymettian marble', 'Hymettos marble', 'Hymettus marble',
        'Thasian marble', 'Thasos marble',
        'Cipollino marble', 'Cipollino verde', 'Karystian marble',
        'Laconian marble', 'Lacedaemonian marble',
        'Doliana marble', 'Skyros marble', 'Larissa marble',
        'Thessalian green stone', 'verde Thessaly',
        'poros', 'piraeus stone', 'piraeus limestone',
        'Aegina stone',
        'Afyon marble', 'Afyon white',
        'Denizli travertine',
        'Bilecik marble',
        'Elazığ cherry marble', 'Elazığ cherry',
        'Burdur beige', 'Burdur marble',
        'Muğla marble', 'Muğla white',
        'Antalya travertine',
        'Cappadocia tuff', 'Cappadocian tuff',
    ],
    'Egyptian_NorthAfrican': [
        'Aswan granite', 'Syene granite', 'red Aswan granite',
        'black Aswan granite', 'grey Aswan granite',
        'Tura limestone', 'Tura stone', 'Mokattam limestone', 'Mokattam stone',
        'Hathor alabaster', 'Egyptian alabaster', 'calcite alabaster',
        'Imperial porphyry', 'porphyry imperiale', 'Mons Porphyrites',
        'Nubian sandstone',
        'Wadi Hammamat graywacke', 'Bekhen stone',
        'Hatnub alabaster',
        'basalt of Fayum',
        'Giza limestone',
        'travertine of Egypt',
    ],
    'Indian': [
        'Makrana marble', 'Makrana white', 'Makrana stone',
        'Chunar sandstone', 'Chunar stone',
        'Agra red sandstone', 'Fatehpur Sikri sandstone',
        'Jodhpur sandstone', 'Jodhpur stone', 'Jodhpur pink',
        'Jaisalmer stone', 'Jaisalmer limestone', 'Jaisalmer yellow',
        'golden limestone', 'golden sandstone',
        'Delhi quartzite', 'Delhi ridge quartzite', 'Alwar quartzite', 'Alwar stone',
        'khondalite', 'Bhubaneswar stone',
        'Porbandar stone', 'Gwalior mint sandstone', 'Bidasar marble', 'Dhrangadhra stone',
        'Rajnagar marble',
        'Dholpur sandstone', 'Dholpur stone', 'Dholpur pink', 'Dholpur red',
        'Bansi Paharpur sandstone', 'Bansi Paharpur stone',
        'Kota stone', 'Kota limestone',
        'Tandur stone', 'Tandur limestone',
        'Shahabad stone', 'Shahabad limestone',
        'Kadappa stone', 'Cuddapah stone', 'Cuddapah slab',
        'Jalore granite', 'Jalor granite',
        'Udaipur green marble', 'Rajasthan green marble',
        'Ambaji marble', 'Ambaji white',
        'Dungri marble',
        'Mandana red stone', 'Mandana stone',
        'Black Galaxy granite', 'Star Galaxy', 'Absolute Black granite',
        'Kashmir White granite', 'Himalayan White granite',
        'Tan Brown granite', 'Multicolor Red', 'Imperial Red',
        'Rajasthan marble', 'Indian marble',
        'Indian sandstone', 'Indian granite', 'Indian limestone',
        'Vindhyan sandstone', 'Bhander sandstone',
    ],
    'Chinese_Japanese_Korean': [
        'Dali marble', 'Yunnan marble', 'Cangshan marble',
        'Fangshan marble', 'Fangshan stone',
        'Qingdao granite',
        'Shanxi black granite', 'Shanxi black',
        'Fujian granite', 'Huian white granite',
        'Laizhou marble',
        'Hebei granite',
        'Lushan stone',
        'Taihu stone', 'Taihu limestone',
        'bluestone', 'blue brick',
        'Ōya stone', 'Oya stone', 'Oya tuff',
        'Aji stone', 'Aji granite',
        'Mikage stone', 'Mikageishi', 'Mikage granite',
        'Inada granite', 'Inada stone',
        'Kitagi granite',
        'Nebukawa stone',
        'Izumi sandstone',
        'Tatsuyama stone',
        'Izu stone',
        'Geochang granite', 'Pocheon granite',
    ],
    'MiddleEastern': [
        'Jerusalem stone', 'Meleke stone', 'Melekeh stone',
        'Jerusalem limestone', 'Jerusalem Gold', 'Jerusalem cream',
        'Hebron stone', 'Hebron limestone',
        'Nari stone', 'Nari limestone',
        'Mizzi Hilu', 'Mizzi Ahmar', 'Mizzi Yahudi',
        'Royal Red', 'Omani marble',
        'Musandam stone', 'Musandam limestone',
        'Riyadh limestone', 'Riyadh stone',
        'Mosul marble',
        'Nimrud stone',
        'Hamadan stone',
        'Isfahan travertine',
        'Persepolis limestone', 'Persepolis stone',
        'Shiraz stone',
        'Tabriz travertine',
    ],
    'American': [
        'Indiana limestone', 'Salem limestone', 'Bedford limestone',
        'Georgia marble', 'Tate marble', 'Cherokee marble',
        'Vermont marble', 'Danby marble', 'Dorset marble',
        'Tennessee marble', 'Tennessee pink', 'Holston marble',
        'Crab Orchard stone', 'Crab Orchard sandstone',
        'Connecticut brownstone', 'Portland brownstone',
        'Pennsylvania bluestone', 'New York bluestone',
        'Berea sandstone', 'Berea stone',
        'Kasota stone', 'Kasota limestone',
        'Minnesota pipestone', 'catlinite',
        'Ohio sandstone', 'Berea grit',
        'Texas limestone', 'Texas cream', 'Texas shell stone',
        'Lueders limestone', 'Austin chalk', 'Austin stone',
        'Carthage marble',
        'Winona stone', 'Mankato stone', 'Mankato limestone',
        'Colorado sandstone', 'Colorado red', 'Lyons sandstone',
        'Fond du Lac stone',
        'Medina sandstone',
        'Joliet limestone',
        'Barre granite', 'Barre grey',
        'Quincy granite',
        'Rockville granite', 'Stony Creek granite',
        'Chelmsford granite',
        'Milford pink granite',
        'cantera rosa',
        'Oaxaca green stone', 'piedra verde',
        'Santo Tomás marble',
    ],
    'African': [
        'Zimbabwean granite', 'Zimbabwe black',
        'South African granite',
        'Nero Impala', 'Impala black',
        'Belfast Black', 'Belfast granite',
        'African Red granite', 'African Red',
        'Rustenburg granite',
        'Pretoria granite',
        'Cape granite',
        'Malawi stone',
        'Kenyan marble',
        'Ethiopian stone',
        'Nubian stone',
    ],
    'Other_Regional': [
        'Jura limestone', 'Jura marble', 'Jura stone',
        'Solnhofen limestone', 'Solnhofen stone',
        'Muschelkalk', 'Muschelkalk limestone',
        'Obernkirchener sandstone', 'Obernkirchen sandstone',
        'Ibbenbüren sandstone',
        'Baumberger sandstone', 'Baumberger stone',
        'Weser sandstone', 'Wesersandstein',
        'Elbsandstein', 'Elbe sandstone', 'Saxon sandstone',
        'Postaer sandstone', 'Cotta sandstone',
        'Pirna sandstone', 'Reinhardtsdorfer sandstone',
        'Heilbronner sandstone', 'Schilfsandstein',
        'Savonnières stone',
        'Euville stone',
        'Belgian granite', 'petit granit', 'Belgian bluestone',
        'Walloon limestone',
        'Rochefort stone', 'Pierre de Rochefort',
        'Meuse stone',
        'Dutch limestone', 'Maastricht limestone', 'Mergel',
        'Bentheimer sandstone', 'Bentheim sandstone',
        'Udelfanger sandstone',
        'Ettringer tuff', 'Weiberner tuff',
        'Niedermendig basalt', 'Mayen basalt',
        'Drachenfels trachyte',
        'Norwegian granite', 'Larvikite', 'Labrador granite',
        'Bohus granite', 'Hallandia granite',
        'Gotland limestone', 'Gotland sandstone',
        'Öland limestone',
        'Finnish granite', 'Baltic Brown',
        'Carrara of the Balkans',
        'Sivec marble', 'Prilep marble',
        'Romanian travertine',
        'Russian granite', 'Karelian granite',
        'Ukrainian granite', 'Labradorite',
    ],
}

# ─────────────────────────────────────────────────────────
# DECORATIVE MINERALS & PRECIOUS/SEMI-PRECIOUS STONES
# ─────────────────────────────────────────────────────────

decorative_minerals = [
    # Precious
    'diamond', 'ruby', 'sapphire', 'emerald',
    # Semi-precious
    'lapis lazuli', 'lapis', 'lazurite',
    'malachite', 'azurite',
    'turquoise',
    'carnelian', 'cornelian', 'sard',
    'agate', 'banded agate', 'moss agate', 'fire agate', 'blue lace agate',
    'onyx', 'sardonyx', 'black onyx',
    'chalcedony', 'chrysoprase', 'bloodstone', 'heliotrope',
    'jasper', 'red jasper', 'green jasper', 'picture jasper',
    'opal', 'fire opal',
    'garnet', 'almandine', 'pyrope', 'rhodolite',
    'amethyst',
    'citrine', 'smoky quartz', 'rose quartz', 'rock crystal', 'quartz crystal',
    'topaz', 'imperial topaz',
    'tourmaline', 'rubellite', 'indicolite', 'verdelite',
    'peridot', 'olivine',
    'zircon', 'hyacinth',
    'spinel', 'balas ruby',
    'beryl', 'aquamarine', 'heliodor', 'morganite',
    'moonstone', 'labradorite', 'sunstone', 'amazonite',
    'feldspar', 'orthoclase',
    'aventurine', 'aventurine quartz',
    'tiger eye', 'tiger\'s eye', 'hawk\'s eye', 'cat\'s eye',
    'obsidian',
    # Ornamental / Construction-decorative
    'mother of pearl', 'nacre', 'mother-of-pearl',
    'coral', 'red coral', 'precious coral',
    'jet', 'Whitby jet',
    'amber', 'Baltic amber', 'copal',
    'nephrite', 'nephrite jade',
    'jadeite', 'jade', 'imperial jade',
    'serpentine', 'bowenite',
    'rhodonite', 'rhodochrosite',
    'sodalite',
    'fluorite', 'fluorspar', 'Blue John',
    'haematite', 'hematite',
    'magnetite',
    'pyrite', 'fool\'s gold', 'marcasite',
    'chalcopyrite',
    'galena',
    'cinnabar', 'vermilion',
    'stibnite',
    'barite', 'baryte',
    'celestine', 'celestite',
    'strontianite',
    'wulfenite',
    'vanadinite',
    'chrysocolla',
    'dioptase',
    'smithsonite',
    'hemimorphite',
    'prehnite',
    'epidote', 'unakite', 'zoisite', 'tanzanite',
    'vesuvianite', 'idocrase',
    'diopside', 'chrome diopside',
    'enstatite',
    'hypersthene',
    'iolite', 'cordierite',
    'kyanite', 'disthene',
    'sillimanite', 'fibrolite',
    'andalusite', 'chiastolite',
    'staurolite', 'fairy cross',
    'chrysoberyl', 'alexandrite',
    'sphene', 'titanite',
    'pietra dura', 'pietre dure', 'parchin kari', 'intarsia',
    'scagliola',
    'opus sectile',
    'cosmati', 'cosmatesque',
    'terrazzo',
]

# ─────────────────────────────────────────────────────────
# GENERAL STONE / CONSTRUCTION TERMS
# ─────────────────────────────────────────────────────────

construction_terms = [
    # Stonework techniques
    'ashlar', 'coursed ashlar', 'random ashlar',
    'rubble', 'coursed rubble', 'random rubble', 'uncoursed rubble',
    'dressed stone', 'rough-hewn', 'rough hewn', 'rough-cut', 'rough cut',
    'cut stone', 'hewn stone', 'wrought stone',
    'dimension stone', 'building stone', 'natural stone',
    'quarry stone', 'quarried stone', 'quarried',
    'freestone', 'brownstone', 'bluestone', 'greystone', 'whitestone',
    'redstone', 'yellowstone',
    'paving stone', 'paver', 'sett', 'cobble',
    'capstone', 'coping stone', 'coping',
    'cornerstone', 'quoin', 'quoin stone',
    'voussoir', 'keystone', 'springer',
    'lintel', 'lintel stone',
    'threshold', 'threshold stone', 'sill', 'sill stone',
    'monolith', 'monolithic',
    'megalith', 'megalithic',
    'orthostat', 'orthostatic',
    'menhir', 'standing stone',
    'stele', 'stela', 'stelae',
    'obelisk',
    'cobblestone', 'cobble stone',
    'fieldstone', 'field stone',
    'whinstone',
    'dry stone', 'drystone', 'dry-stone',
    'cyclopean', 'cyclopean masonry', 'polygonal masonry',
    'opus incertum', 'opus reticulatum', 'opus vittatum',
    'opus caementicium', 'opus testaceum', 'opus mixtum',
    'opus quadratum', 'opus spicatum',
    'opus signinum', 'opus sectile',
    'rustication', 'rusticated', 'bossage', 'vermiculation',
    'pointing', 'repointing', 'tuck pointing',
    'coursing', 'bond', 'stretcher bond', 'header bond', 'Flemish bond',
    'English bond', 'stack bond', 'running bond',
    'pier', 'pilaster', 'engaged column', 'half-column',
    'plinth', 'pedestal', 'socle', 'stylobate', 'stereobate',
    'crepidoma',
    'dado', 'wainscot',
    'baluster', 'balustrade', 'newel',
    'parapet', 'battlement', 'crenellation', 'merlon', 'crenel',
    'machicolation', 'brattice',
    'turret', 'bartisan', 'oriel',
    'pinnacle', 'finial', 'crocket',
    'gargoyle', 'grotesque', 'chimera',
    'tracery', 'bar tracery', 'plate tracery',
    'mullion', 'transom', 'muntins',
    'tympanum', 'lunette',
    'rose window', 'wheel window', 'oculus',
    'lancet', 'lancet window', 'ogee', 'ogive',
    'trefoil', 'quatrefoil', 'cinquefoil', 'multifoil',
    'architrave', 'entablature', 'cornice', 'frieze',
    'capital', 'abacus', 'echinus', 'volute', 'fluting',
    'Doric', 'Ionic', 'Corinthian', 'Tuscan', 'Composite',
    'pediment', 'broken pediment', 'triangular pediment',
    'acanthus', 'palmette', 'anthemion',
    'arabesque', 'interlace', 'guilloche', 'fret', 'meander',
    'dentil', 'modillion', 'mutule', 'triglyph', 'metope',
    'stonemasonry', 'stone masonry', 'stonemason', 'stone mason',
    'stonecutter', 'stone cutter', 'stone carver', 'stone carving',
    'masonry', 'masoned', 'mason',
    'blockwork', 'block work', 'block stone',
    'cladding', 'veneer', 'stone veneer', 'facing',
    'revetment', 'stone revetment',
]

# ─────────────────────────────────────────────────────────
# BUILDING MATERIALS (Non-stone)
# ─────────────────────────────────────────────────────────

building_materials = [
    # Binding agents
    'mortar', 'lime mortar', 'hydraulic lime', 'hydraulic mortar',
    'cement', 'Portland cement', 'Roman cement', 'pozzolanic cement',
    'concrete', 'reinforced concrete', 'precast concrete', 'prestressed concrete',
    'Roman concrete', 'opus caementicium',
    'plaster', 'lime plaster', 'gypsum plaster', 'cement plaster',
    'stucco', 'stucco lustro', 'sgraffito',
    'render', 'rendering', 'harling', 'roughcast', 'pebbledash',

    # Brick & tile
    'brick', 'fired brick', 'kiln-fired brick',
    'sun-dried brick', 'sun dried brick', 'unfired brick',
    'mud brick', 'mud-brick', 'mudbrick',
    'glazed brick', 'polychrome brick', 'moulded brick',
    'Roman brick', 'thin brick', 'clinker brick',
    'engineering brick', 'facing brick', 'common brick',
    'tile', 'roof tile', 'floor tile', 'wall tile',
    'glazed tile', 'encaustic tile', 'quarry tile',
    'terracotta', 'terra cotta', 'terracotta tile',
    'faience', 'majolica', 'maiolica',
    'zellige', 'zellij',
    'azulejo', 'azulejos',
    'Iznik tile', 'Iznik ceramic',
    'Delft tile', 'Delft ware',
    'ceramic', 'ceramics', 'porcelain', 'stoneware', 'earthenware',

    # Earth
    'adobe', 'adobe brick', 'adobe block',
    'rammed earth', 'pisé', 'pise', 'tapia', 'tabby',
    'wattle and daub', 'wattle-and-daub', 'wattle & daub',
    'cob', 'cob wall',
    'clay', 'fired clay', 'unfired clay',
    'mud wall', 'earth wall', 'earth building',
    'compressed earth block', 'stabilized earth',

    # Wood/timber
    'timber', 'timber frame', 'timber-frame', 'timber-framed',
    'half-timber', 'half-timbered', 'fachwerk',
    'wood', 'wooden', 'hardwood', 'softwood',
    'oak', 'teak', 'mahogany', 'cedar', 'pine', 'cypress',
    'ebony', 'rosewood', 'walnut', 'chestnut', 'elm', 'ash',
    'bamboo', 'rattan',
    'log', 'log cabin', 'log house',
    'shingle', 'wood shingle', 'shake',
    'post and beam', 'post-and-beam',
    'stave', 'stave church',

    # Metal
    'iron', 'wrought iron', 'cast iron', 'pig iron',
    'steel', 'structural steel', 'stainless steel',
    'bronze', 'bell bronze',
    'copper', 'copper roof', 'copper dome', 'copper cladding',
    'lead', 'lead roof', 'lead cladding', 'lead sheet',
    'zinc', 'zinc roof',
    'tin', 'tinplate', 'tin roof',
    'gold', 'gold leaf', 'gilding', 'gilt',
    'silver', 'silver leaf',

    # Glass
    'glass', 'stained glass', 'plate glass', 'crown glass',
    'blown glass', 'leaded glass', 'painted glass',
    'window glass', 'cathedral glass',

    # Roofing
    'thatch', 'thatched', 'reed', 'straw',
    'slate roof', 'tile roof', 'shingle roof',
    'pantile', 'imbrex', 'tegula',

    # Mosaic / decorative
    'mosaic', 'tessera', 'tesserae', 'opus tessellatum', 'opus vermiculatum',
    'fresco', 'fresco secco', 'buon fresco', 'al fresco',
    'inlay', 'stone inlay', 'marble inlay',
    'marquetry', 'parquetry', 'intarsia',
    'lacquer', 'lacquerwork',
    'enamel', 'cloisonné', 'champlevé',
    'ivory', 'bone', 'horn',
    'shell', 'mother-of-pearl', 'nacre',
    'semi-precious', 'precious stone', 'gemstone', 'gem',
    'pietra dura', 'pietre dure', 'commesso',
    'scagliola',
    'terrazzo', 'granito', 'Venetian terrazzo',
    'smalti', 'smalt',
]

# ─────────────────────────────────────────────────────────
# ARCHITECTURE TERMS & STYLES
# ─────────────────────────────────────────────────────────

architecture_terms = [
    'architecture', 'architectural', 'edifice', 'structure', 'building',
    'construction', 'masonry', 'monument', 'monumental', 'façade', 'facade',
    'elevation', 'plan', 'design', 'layout',
    # Western historical styles
    'romanesque', 'gothic', 'early gothic', 'high gothic', 'late gothic',
    'flamboyant gothic', 'rayonnant', 'perpendicular gothic', 'decorated gothic',
    'baroque', 'high baroque', 'late baroque',
    'renaissance', 'early renaissance', 'high renaissance',
    'neoclassical', 'neo-classical', 'classicism',
    'art deco', 'art nouveau', 'jugendstil', 'sezession', 'liberty style',
    'modernist', 'modern movement', 'international style',
    'brutalist', 'brutalism',
    'beaux-arts', 'beaux arts', 'ecole des beaux-arts',
    'rococo', 'rococó',
    'mannerist', 'mannerism',
    # Regional styles
    'byzantine', 'neo-byzantine',
    'ottoman', 'ottoman classical',
    'mughal', 'moghul',
    'moorish', 'neo-moorish',
    'mudéjar', 'mudejar',
    'plateresque', 'manueline',
    'isabelline', 'herrerian', 'churrigueresque',
    'norman', 'anglo-norman', 'romanesque-norman',
    'tudor', 'elizabethan', 'jacobean', 'stuart',
    'georgian', 'regency', 'queen anne',
    'victorian', 'edwardian',
    'palladian', 'neo-palladian',
    'colonial', 'colonial baroque', 'indo-saracenic',
    'vernacular', 'traditional', 'indigenous',
    'dravidian', 'nagara', 'vesara', 'kalinga',
    'khmer', 'cham', 'javanese',
    'sino-tibetan', 'tang dynasty', 'song dynasty', 'ming dynasty',
    'qing dynasty', 'han dynasty',
    'Edo period', 'Nara period', 'Heian period',
    'joseon', 'goryeo', 'silla',
    'safavid', 'timurid', 'seljuk', 'abbasid', 'umayyad', 'fatimid',
    'mamluk', 'ayyubid', 'almoravid', 'almohad',
    'constructivist', 'constructivism',
    'deconstructivist', 'deconstructivism',
    'expressionist', 'expressionism',
    'organic architecture',
    'metabolist', 'metabolism',
    'postmodern', 'postmodernist', 'post-modern',
    'high-tech architecture', 'structural expressionism',
]

# ─────────────────────────────────────────────────────────
# CONSTRUCTION VERBS & ACTIONS
# ─────────────────────────────────────────────────────────

construction_verbs = [
    'built', 'constructed', 'erected', 'carved', 'sculpted', 'hewn',
    'quarried', 'assembled', 'crafted', 'chiseled', 'chiselled',
    'mortared', 'plastered', 'rendered', 'vaulted', 'domed', 'arched',
    'buttressed', 'fortified', 'walled', 'tiled', 'paved', 'roofed',
    'foundations', 'stonework', 'brickwork', 'woodwork', 'metalwork',
    'ironwork', 'commissioned', 'designed', 'rebuilt', 'restored',
    'renovated', 'remodelled', 'reconstructed', 'enlarged', 'extended',
    'embellished', 'ornamented', 'decorated', 'gilded', 'painted',
    'inscribed', 'engraved', 'incised', 'sculpted', 'moulded', 'molded',
    'fabricated', 'forged', 'cast', 'wrought', 'hammered', 'riveted',
    'cemented', 'grouted', 'pointed', 'caulked', 'sealed',
    'underpinned', 'reinforced', 'shored',
    'quarrying', 'mining', 'excavating', 'dressing', 'polishing',
    'laying', 'coursing', 'bonding', 'cladding', 'facing',
    'veneering', 'panelling', 'paneling',
]

# ─────────────────────────────────────────────────────────
# ARCHITECTURAL ELEMENTS
# ─────────────────────────────────────────────────────────

architectural_elements = [
    'column', 'pillar', 'pier', 'arch', 'vault', 'dome', 'cupola',
    'spire', 'buttress', 'flying buttress', 'cornice', 'frieze',
    'pediment', 'capital', 'entablature', 'lintel', 'keystone',
    'voussoir', 'balustrade', 'parapet', 'crenellation', 'merlon',
    'machicolation', 'portcullis', 'drawbridge', 'moat', 'turret',
    'pinnacle', 'finial', 'gargoyle', 'tracery', 'rose window',
    'apse', 'nave', 'transept', 'chancel', 'altar', 'ambulatory',
    'clerestory', 'triforium', 'narthex', 'atrium', 'courtyard',
    'gallery', 'balcony', 'terrace', 'staircase', 'minbar',
    'mihrab', 'muqarnas', 'stalactite vault', 'iwan', 'pishtaq',
    'jali', 'lattice', 'screen', 'portico', 'peristyle',
    'hypostyle', 'cella', 'pronaos', 'stylobate',
    'fluting', 'volute', 'acanthus', 'arabesque', 'ogee',
    'trefoil', 'quatrefoil', 'lancet', 'mullion', 'transom',
    'tympanum', 'architrave', 'corbel', 'bracket', 'cantilever',
    'truss', 'beam', 'rafter', 'roof', 'ceiling', 'floor',
    'wall', 'foundation', 'plinth', 'podium', 'base', 'shaft',
    'abacus', 'echinus',
    'pendentive', 'squinch', 'tambour', 'drum',
    'lantern', 'oculus', 'skylight', 'dormer',
    'gable', 'hip roof', 'mansard', 'gambrel',
    'cloister', 'ambulatory', 'chapter house', 'refectory',
    'sacristy', 'vestry', 'baptistry',
    'minaret', 'muezzin', 'qibla',
    'shikhara', 'vimana', 'gopura', 'mandapa', 'garbhagriha',
    'torana', 'chattra', 'harmika', 'anda',
    'pagoda', 'dagoba', 'chorten', 'candi',
]

# ─────────────────────────────────────────────────────────
# EXCLUSION KEYWORDS (Non-built heritage)
# ─────────────────────────────────────────────────────────

exclusion_keywords = [
    'cultural landscape', 'rock art', 'cave painting', 'cave art',
    'petroglyph', 'pictograph', 'geoglyph',
    'vineyard', 'terrace farming', 'rice terrace',
    'agave landscape', 'coffee landscape', 'tea landscape',
    'fossil', 'hominid', 'hominin', 'paleontological', 'palaeontological',
    'oral tradition', 'intangible',
    'prehistoric art', 'engravings',
    'textile', 'weaving',
    'agricultural', 'pastoral', 'nomadic',
]


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CLASSIFICATION ENGINE                                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Flatten all named stones into a single list for matching
all_named_stones = []
for region, stones in named_stones.items():
    all_named_stones.extend(stones)

# Combine all stone/rock lists
all_geological_stones = igneous_rocks + sedimentary_rocks + metamorphic_rocks

_REGEX_CACHE = {}

def find_matches(lemmatized_text, keyword_list):
    """Find keywords using NLP lemmatization and strict regex boundaries to prevent false positives (e.g., 'opal' in 'Episcopal')."""
    matches = []
    for kw in keyword_list:
        kw_lower = kw.lower()
        if kw_lower not in _REGEX_CACHE:
            _REGEX_CACHE[kw_lower] = re.compile(r'\b' + re.escape(kw_lower) + r'\b')
        if _REGEX_CACHE[kw_lower].search(lemmatized_text):
            matches.append(kw)
    return list(set(matches))

def classify_geological(matched_stones):
    """Determine which geological classes a site's stones fall into."""
    classes = set()
    for stone in matched_stones:
        sl = stone.lower()
        if sl in [s.lower() for s in igneous_rocks]:
            classes.add('Igneous')
        elif sl in [s.lower() for s in sedimentary_rocks]:
            classes.add('Sedimentary')
        elif sl in [s.lower() for s in metamorphic_rocks]:
            classes.add('Metamorphic')
    return classes

def classify_site(row):
    site_name = str(row.get('site_name', '')).lower()
    ouv = str(row.get('ouv_statement', '')).lower()
    criteria = str(row.get('criteria', '')).lower()
    short_desc = str(row.get('short_description', '')).lower() if 'short_description' in row.index else ''
    combined_text = ouv + ' ' + short_desc + ' ' + site_name

    # NLP tokenization & lemmatization (done ONCE per site for massive speedup)
    words = word_tokenize(combined_text)
    lemmatized_words = [lemmatizer.lemmatize(w.lower()) for w in words]
    lemmatized_text = " ".join(lemmatized_words)

    score = 0
    matched_categories = []
    matched_name_kws = []

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

    # ── LAYER 2: Site name keyword matching ──
    for category, keywords in name_keywords.items():
        for kw in keywords:
            if len(kw) <= 4:
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, site_name):
                    score += 3
                    matched_categories.append(f'Name_{category}')
                    matched_name_kws.append(kw)
                    break
            else:
                if kw in site_name:
                    score += 3
                    matched_categories.append(f'Name_{category}')
                    matched_name_kws.append(kw)
                    break

    # ── LAYER 3: STONE-HEAVY OUV TEXT ANALYSIS ──

    # 3a. Geological stone types
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

    # 3b. Named/Trade stones (HIGHEST weight - very specific)
    named_stone_matches = find_matches(lemmatized_text, all_named_stones)
    if len(named_stone_matches) >= 1:
        score += 5
        matched_categories.append('Named_Stone')
    if len(named_stone_matches) >= 3:
        score += 3
        matched_categories.append('Named_Stone_3+')

    # 3c. Decorative minerals
    deco_matches = find_matches(lemmatized_text, decorative_minerals)
    if len(deco_matches) >= 1:
        score += 2
        matched_categories.append('Decorative_Mineral')
    if len(deco_matches) >= 3:
        score += 2
        matched_categories.append('Decorative_Mineral_3+')

    # 3d. Construction terms
    constr_matches = find_matches(lemmatized_text, construction_terms)
    if len(constr_matches) >= 2:
        score += 2
        matched_categories.append('OUV_Construction')
    if len(constr_matches) >= 5:
        score += 2
        matched_categories.append('OUV_Construction_5+')

    # 3e. Building materials
    mat_matches = find_matches(lemmatized_text, building_materials)
    if len(mat_matches) >= 2:
        score += 2
        matched_categories.append('OUV_Materials')
    if len(mat_matches) >= 5:
        score += 2
        matched_categories.append('OUV_Materials_5+')

    # 3f. Architectural elements
    elem_matches = find_matches(lemmatized_text, architectural_elements)
    if len(elem_matches) >= 3:
        score += 3
        matched_categories.append('OUV_ArchElements')
    if len(elem_matches) >= 6:
        score += 2
        matched_categories.append('OUV_ArchElements_6+')

    # 3g. Architecture terms / styles
    style_matches = find_matches(lemmatized_text, architecture_terms)
    if len(style_matches) >= 2:
        score += 2
        matched_categories.append('OUV_ArchTerms')

    # 3h. Construction verbs
    verb_matches = find_matches(lemmatized_text, construction_verbs)
    if len(verb_matches) >= 2:
        score += 2
        matched_categories.append('OUV_ConstructionVerbs')

    # ── LAYER 4: Exclusion check ──
    exclusion_hit = False
    for ex_kw in exclusion_keywords:
        if ex_kw in site_name:
            exclusion_hit = True
            break
    if exclusion_hit:
        score = max(0, score - 3)

    # ── MANUAL OVERRIDES FOR MAJOR SITES WHERE UNESCO TEXT OMITS STONES ──
    manual_overrides = {
        "taj mahal": ["Makrana marble"],
        "piazza del duomo, pisa": ["Carrara marble"],
        "historic centre of florence": ["Carrara marble"],
        "city of verona": ["Carrara marble"]
    }
    for site, override_stones in manual_overrides.items():
        if site in site_name:
            for s in override_stones:
                if s not in named_stone_matches:
                    named_stone_matches.append(s)
                    matched_categories.append('Named_Stone_Override')
                    score += 5

    # ── Geological classification of found stones ──
    all_stone_matches = list(set(geo_stone_matches + named_stone_matches))
    geo_classes = classify_geological(all_stone_matches)

    # ── Determine confidence tier ──
    if score >= 10:
        confidence = 'HIGH'
    elif score >= 5:
        confidence = 'MEDIUM'
    elif score >= 1:
        confidence = 'LOW'
    else:
        confidence = 'NONE'

    return pd.Series({
        'confidence': confidence,
        'score': score,
        'stone_count': len(all_stone_matches),
        'stone_types_found': '; '.join(sorted(all_stone_matches)),
        'stone_geological_class': '; '.join(sorted(geo_classes)),
        'named_trade_stones': '; '.join(sorted(named_stone_matches)),
        'decorative_minerals_found': '; '.join(sorted(deco_matches)),
        'building_materials_found': '; '.join(sorted(mat_matches)),
        'construction_terms_found': '; '.join(sorted(constr_matches)),
        'architectural_elements_found': '; '.join(sorted(elem_matches)),
        'architecture_style_found': '; '.join(sorted(style_matches)),
        'construction_verbs_found': '; '.join(sorted(verb_matches)),
        'matched_categories': '; '.join(matched_categories),
        'matched_name_keywords': '; '.join(matched_name_kws),
    })


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  RUN CLASSIFICATION                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

print(f"Classifying {len(df)} cultural sites with enriched stone dictionary...")
print(f"Dictionary sizes:")
print(f"  Igneous rocks:       {len(igneous_rocks)} entries")
print(f"  Sedimentary rocks:   {len(sedimentary_rocks)} entries")
print(f"  Metamorphic rocks:   {len(metamorphic_rocks)} entries")
print(f"  Named/Trade stones:  {len(all_named_stones)} entries")
print(f"  Decorative minerals: {len(decorative_minerals)} entries")
print(f"  Construction terms:  {len(construction_terms)} entries")
print(f"  Building materials:  {len(building_materials)} entries")
print(f"  Architecture terms:  {len(architecture_terms)} entries")
print(f"  Construction verbs:  {len(construction_verbs)} entries")
print(f"  Arch. elements:      {len(architectural_elements)} entries")
total_dict = len(igneous_rocks) + len(sedimentary_rocks) + len(metamorphic_rocks) + len(all_named_stones) + len(decorative_minerals) + len(construction_terms) + len(building_materials) + len(architecture_terms) + len(construction_verbs) + len(architectural_elements)
print(f"  ─────────────────────────────────")
print(f"  TOTAL DICTIONARY:    {total_dict} entries")
print()

# Run the classification via tqdm for progress tracking
tqdm.pandas()
results = df.progress_apply(classify_site, axis=1)
df_classified = pd.concat([df, results], axis=1)

# Format the UNESCO URLs automatically!
if 'unesco_url' in df_classified.columns:
    df_classified['unesco_url'] = 'https://whc.unesco.org/en/list/' + df_classified['unesco_id'].astype(str)

df_classified = df_classified.sort_values('score', ascending=False)

# Save full classified dataset
df_classified.to_csv('Imp Data/cultural_sites_classified.csv', index=False)

# Save only the built monument sites (HIGH and MEDIUM confidence)
built_monuments = df_classified[df_classified['confidence'].isin(['HIGH', 'MEDIUM'])]
built_monuments.to_csv('Imp Data/built_monument_sites.csv', index=False)

# Print statistics
print(f"{'='*60}")
print(f"CLASSIFICATION RESULTS")
print(f"{'='*60}")
print(f"Total Cultural Sites Analyzed: {len(df)}")
print()
print(f"HIGH Confidence (Built Monuments):   {len(df_classified[df_classified['confidence']=='HIGH'])}")
print(f"MEDIUM Confidence:                   {len(df_classified[df_classified['confidence']=='MEDIUM'])}")
print(f"LOW Confidence:                      {len(df_classified[df_classified['confidence']=='LOW'])}")
print(f"NONE (Not built structures):         {len(df_classified[df_classified['confidence']=='NONE'])}")
print()
print(f"Total Built Monument Sites (HIGH+MEDIUM): {len(built_monuments)}")
print(f"{'='*60}")

# Stone-specific stats
has_stones = df_classified[df_classified['stone_count'] > 0]
print(f"\n{'='*60}")
print(f"STONE ANALYSIS")
print(f"{'='*60}")
print(f"Sites mentioning at least 1 stone/rock: {len(has_stones)}")
print(f"Sites with named/trade stones:          {len(df_classified[df_classified['named_trade_stones'].str.len() > 0])}")
print(f"Sites with decorative minerals:         {len(df_classified[df_classified['decorative_minerals_found'].str.len() > 0])}")
print(f"Average stones per site (where >0):     {has_stones['stone_count'].mean():.1f}")
print(f"Max stones mentioned in a single site:  {df_classified['stone_count'].max()}")

# Top 15 stone-richest sites
print(f"\nTop 15 Stone-Richest Sites:")
top_stone = df_classified.nlargest(15, 'stone_count')
for _, r in top_stone.iterrows():
    print(f"  [{r['stone_count']} stones, score {r['score']}] {r['site_name']}")
    print(f"    Stones: {r['stone_types_found'][:100]}...")

print(f"\nTop 10 HIGH confidence sites by score:")
high = df_classified[df_classified['confidence']=='HIGH'].head(10)
for _, r in high.iterrows():
    print(f"  [{r['score']}] {r['site_name']}")
    print(f"    Categories: {r['matched_categories'][:80]}")

print(f"\nSample LOW/NONE sites (to review for missed monuments):")
low_none = df_classified[df_classified['confidence'].isin(['LOW', 'NONE'])].tail(15)
for _, r in low_none.iterrows():
    print(f"  [{r['confidence']}, score {r['score']}] {r['site_name']}")
