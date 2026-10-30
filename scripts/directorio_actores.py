"""Construye data/instituciones.json (directorio de actores) a partir de los capítulos.

Fuentes por capítulo: tabla de organización anfitriona / co-anfitriona, lista de
conferencistas y afiliaciones de autores (front matter). Una institución se detecta
con los patrones de REGISTRO; un patrón con prefijo "=" distingue mayúsculas (siglas).

Uso:  python3 scripts/directorio_actores.py [--huerfanos]
"""
import glob, json, re, sys, unicodedata, yaml

ROOT = "."
SALIDA = "data/instituciones.json"
PREVIO = "data/instituciones_base.json"  # 33 instituciones originales con descripción

COLOR = {
    "Gobierno nacional": "primary", "Gobierno territorial": "success",
    "Autoridad ambiental": "success", "Internacional": "info", "Humanitaria": "danger",
    "Academia nacional": "warning", "Academia internacional": "warning",
    "Gremio técnico": "secondary", "Organización técnica": "secondary",
    "Sociedad civil": "dark", "Sector privado": "secondary",
}
ORDEN_TIPOS = list(COLOR)

GN, GT, AA, IN, HU = "Gobierno nacional", "Gobierno territorial", "Autoridad ambiental", "Internacional", "Humanitaria"
AN, AI, GR, OT, SC, SP = "Academia nacional", "Academia internacional", "Gremio técnico", "Organización técnica", "Sociedad civil", "Sector privado"

# (sigla, nombre, tipo, [patrones])
REGISTRO = [
    ("UNGRD", "Unidad Nacional para la Gestión del Riesgo de Desastres", GN, ["=UNGRD", "Unidad Nacional para la Gestion del Riesgo", "Unidad Nacional de Gestion del Riesgo"]),
    ("SGC", "Servicio Geológico Colombiano", GN, ["=SGC", "Servicio Geologico Colombiano"]),
    ("IDEAM", "Instituto de Hidrología, Meteorología y Estudios Ambientales", GN, ["=IDEAM", "=Ideam", "Instituto de Hidrologia, Meteorologia", "Instituto de Estudios Ambientales"]),
    ("IGAC", "Instituto Geográfico Agustín Codazzi", GN, ["=IGAC", "Agustin Codazzi"]),
    ("DANE", "Departamento Administrativo Nacional de Estadística", GN, ["=DANE", "Departamento Administrativo Nacional de Estadistica"]),
    ("DNP", "Departamento Nacional de Planeación", GN, ["=DNP", "Departamento Nacional de Planeacion"]),
    ("MinCiencias", "Ministerio de Ciencias, Tecnología e Innovación", GN, ["MinCiencias", "Ministerio de Ciencia"]),
    ("MinTIC", "Ministerio de Tecnologías de la Información y las Comunicaciones", GN, ["MinTIC"]),
    ("DIMAR", "Dirección General Marítima", GN, ["=DIMAR", "Direccion General Maritima"]),
    ("Defensa Civil", "Defensa Civil Colombiana", GN, ["Defensa Civil"]),
    ("Bomberos", "Bomberos Colombia", GN, ["Bomberos", "=DNBC"]),
    ("INVEMAR", "Instituto de Investigaciones Marinas y Costeras", GN, ["INVEMAR", "Investigaciones Marinas y Costeras"]),
    ("Fondo Adaptación", "Fondo Adaptación", GN, ["Fondo Adaptacion"]),
    ("MinAmbiente", "Ministerio de Ambiente y Desarrollo Sostenible", GN, ["MinAmbiente", "=MADS", "Ministerio de Ambiente", "MINAMBIENTE"]),
    ("MinAgricultura", "Ministerio de Agricultura y Desarrollo Rural", GN, ["=MADR", "Ministerio de Agricultura"]),
    ("MinSalud", "Ministerio de Salud y Protección Social", GN, ["Ministerio de Salud"]),
    ("MinEducación", "Ministerio de Educación Nacional", GN, ["Ministerio de Educacion"]),
    ("MinTransporte", "Ministerio de Transporte", GN, ["Ministerio de Transporte", "Mintrasporte"]),
    ("MinVivienda", "Ministerio de Vivienda, Ciudad y Territorio", GN, ["Ministerio de Vivienda", "=MVCT", "Minvivienda"]),
    ("MinMinas", "Ministerio de Minas y Energía", GN, ["Ministerio de Minas"]),
    ("MinIgualdad", "Ministerio de Igualdad y Equidad", GN, ["Ministerio de Igualdad"]),
    ("Mincomercio", "Ministerio de Comercio, Industria y Turismo", GN, ["Mincomercio"]),
    ("INVIAS", "Instituto Nacional de Vías", GN, ["Invias", "INVIAS", "Instituto Nacional de Vias"]),
    ("ANI", "Agencia Nacional de Infraestructura", GN, ["=ANI", "Agencia Nacional de Infraestructura"]),
    ("ICBF", "Instituto Colombiano de Bienestar Familiar", GN, ["=ICBF"]),
    ("ARN", "Agencia para la Reincorporación y la Normalización", GN, ["=ARN", "Agencia para la Reincorporacion"]),
    ("PNN", "Parques Nacionales Naturales de Colombia", GN, ["Parques Nacionales", "=PNN"]),
    ("Aerocivil", "Aeronáutica Civil", GN, ["Aeronautica Civil"]),
    ("Superservicios", "Superintendencia de Servicios Públicos Domiciliarios", GN, ["Superintendencia de Servicios Publicos"]),
    ("Defensoría", "Defensoría del Pueblo", GN, ["Defensoria del Pueblo"]),
    ("CCO", "Comisión Colombiana del Océano", GN, ["=CCO", "Comision Colombiana del Oceano"]),
    ("INCI", "Instituto Nacional para Ciegos", GN, ["=INCI"]),
    ("INSOR", "Instituto Nacional para Sordos", GN, ["=INSOR"]),
    ("Ejército", "Ejército Nacional de Colombia", GN, ["Ejercito Nacional", "Escuela de Ingenieros Militares", "=ESING"]),
    ("Área Metro", "Área Metropolitana del Valle de Aburrá", GT, ["Area Metropolitana"]),
    ("IDIGER", "Instituto Distrital de Gestión de Riesgos y Cambio Climático", GT, ["IDIGER"]),
    ("Casanare", "Gobernación de Casanare", GT, ["Casanare — Consejo", "Gobernacion de Casanare", "Gobernador de Casanare", "Hato Corozal"]),
    ("UAEGRD Boyacá", "Unidad Administrativa Especial para la Gestión del Riesgo de Desastres de Boyacá", GT, ["UAEGRD"]),
    ("Guaranda", "Alcaldía de Guaranda (Sucre)", GT, ["Alcaldia de Guaranda"]),
    ("San Andrés", "Gobernación de San Andrés, Providencia y Santa Catalina", GT, ["San Andres, Providencia"]),
    ("CORNARE", "Corporación Autónoma Regional de las Cuencas de los Ríos Negro y Nare", AA, ["CORNARE"]),
    ("CORPOGUAJIRA", "Corporación Autónoma Regional de La Guajira", AA, ["Corpoguajira", "CORPOGUAJIRA", "Regional de La Guajira"]),
    ("CORPONOR", "Corporación Autónoma Regional de la Frontera Nororiental", AA, ["CORPONOR"]),
    ("CORPOAMAZONIA", "Corporación para el Desarrollo Sostenible del Sur de la Amazonia", AA, ["CORPOAMAZONIA"]),
    ("CORPOBOYACÁ", "Corporación Autónoma Regional de Boyacá", AA, ["CORPOBOYACA"]),
    ("CORPOCALDAS", "Corporación Autónoma Regional de Caldas", AA, ["CORPOCALDAS", "Regional de Caldas"]),
    ("CARDER", "Corporación Autónoma Regional de Risaralda", AA, ["CARDER", "Regional de Risaralda"]),
    ("CRA", "Corporación Autónoma Regional del Atlántico", AA, ["Autonoma Regional del Atlantico"]),
    ("CVC", "Corporación Autónoma Regional del Valle del Cauca", AA, ["=CVC", "Regional del Valle del Cauca"]),
    ("CAR Cundinamarca", "Corporación Autónoma Regional de Cundinamarca", AA, ["CAR Cundinamarca"]),
    ("SDA", "Secretaría Distrital de Ambiente", AA, ["Secretaria Distrital de Ambiente", "=SDA"]),
    ("Instituto Humboldt", "Instituto de Investigación de Recursos Biológicos Alexander von Humboldt", AA, ["Humboldt"]),
    ("ASOCARS", "Asociación de Corporaciones Autónomas Regionales y de Desarrollo Sostenible", AA, ["ASOCARS"]),
    ("PNUD", "Programa de las Naciones Unidas para el Desarrollo", IN, ["PNUD"]),
    ("OCHA", "Oficina de Coordinación de Asuntos Humanitarios", IN, ["OCHA"]),
    ("ONU Mujeres", "ONU Mujeres", IN, ["ONU Mujeres"]),
    ("WMO", "Organización Meteorológica Mundial", IN, ["=OMM", "=WMO", "Organizacion Meteorologica Mundial"]),
    ("Banco Mundial", "Banco Mundial", IN, ["Banco Mundial", "World Bank"]),
    ("USAID", "Agencia de los Estados Unidos para el Desarrollo Internacional", IN, ["USAID"]),
    ("UNDRR", "Oficina de la ONU para la Reducción del Riesgo de Desastres", IN, ["UNDRR", "Reduccion del Riesgo de Desastres (UNDRR"]),
    ("FAO", "Organización de las Naciones Unidas para la Alimentación y la Agricultura", IN, ["=FAO", "Alimentacion y la Agricultura"]),
    ("OIM", "Organización Internacional para las Migraciones", IN, ["=OIM", "Organizacion Internacional para las Migraciones"]),
    ("OPS", "Organización Panamericana de la Salud", IN, ["=OPS", "Organizacion Panamericana de la Salud"]),
    ("PMA", "Programa Mundial de Alimentos", IN, ["=PMA"]),
    ("JICA", "Agencia de Cooperación Internacional del Japón", IN, ["JICA"]),
    ("CDEMA", "Agencia del Caribe para el Manejo de Emergencias y Desastres", IN, ["CDEMA"]),
    ("GIZ", "Cooperación Alemana (GIZ)", IN, ["=GIZ"]),
    ("Unión Europea", "Delegación de la Unión Europea en Colombia", IN, ["Union Europea"]),
    ("CopernicusLAC", "Centro CopernicusLAC Panamá", IN, ["CopernicusLAC"]),
    ("CDRI", "Coalición para la Infraestructura Resiliente a los Desastres", IN, ["=CDRI"]),
    ("CIIFEN", "Centro Internacional para la Investigación del Fenómeno de El Niño", IN, ["CIIFEN"]),
    ("Red LAC Mujeres RRD", "Red de las Américas y el Caribe de Mujeres para la RRD", IN, ["Red LAC", "Red de las Americas y el Caribe de Mujeres", "REDLAC"]),
    ("Anticipation Hub", "Anticipation Hub / Centro del Clima de la Cruz Roja", IN, ["Anticipation Hub", "GTAA"]),
    ("HeiGIT / HOT", "Humanitarian OpenStreetMap — HeiGIT", IN, ["HeiGIT", "Humanitarian OpenStreetMap"]),
    ("3IS", "3IS", IN, ["=3IS"]),
    ("GNDR", "Red Global de Organizaciones de la Sociedad Civil para la Reducción del Riesgo de Desastres", IN, ["=GNDR", "Red Global de la Sociedad Civil", "Red Global de Organizaciones"]),
    ("ICLEI", "ICLEI — Gobiernos Locales por la Sustentabilidad", IN, ["ICLEI"]),
    ("Cruz Roja", "Cruz Roja Colombiana", HU, ["Cruz Roja Colombiana", "Cruz Roja Seccional"]),
    ("IFRC", "Federación Internacional de la Cruz Roja y de la Media Luna Roja", HU, ["Federacion Internacional de la Cruz Roja", "=IFRC"]),
    ("Save the Children", "Save the Children Colombia", HU, ["Save the Children"]),
    ("CARE", "CARE Colombia", HU, ["CARE Colombia"]),
    ("HI", "Humanity & Inclusion", HU, ["Humanity & Inclusion", "Humanity and Inclusion"]),
    ("Mercy Corps", "Mercy Corps", HU, ["Mercy Corps"]),
    ("Start Network", "Start Network", HU, ["Start Network"]),
    ("CESVI", "CESVI", HU, ["CESVI"]),
    ("Scouts", "Scouts de Colombia", HU, ["Scouts de Colombia", "Scout Movement"]),
    ("Uniandes", "Universidad de los Andes", AN, ["Universidad de los Andes"]),
    ("UNAL", "Universidad Nacional de Colombia", AN, ["Universidad Nacional de Colombia", "Universidad Nacional,", "=UNAL", "ORFE – Universidad Nacional"]),
    ("EAFIT", "Universidad EAFIT", AN, ["EAFIT"]),
    ("Javeriana", "Pontificia Universidad Javeriana", AN, ["Javeriana"]),
    ("U. Antioquia", "Universidad de Antioquia", AN, ["Universidad de Antioquia"]),
    ("EIA", "Universidad EIA", AN, ["Universidad EIA"]),
    ("U. Rosario", "Universidad del Rosario", AN, ["Universidad del Rosario"]),
    ("UIS", "Universidad Industrial de Santander", AN, ["Universidad Industrial de Santander"]),
    ("U. Caldas", "Universidad de Caldas", AN, ["Universidad de Caldas"]),
    ("UTP", "Universidad Tecnológica de Pereira", AN, ["Universidad Tecnologica de Pereira"]),
    ("U. Metropolitana", "Universidad Metropolitana (Barranquilla)", AN, ["Universidad Metropolitana"]),
    ("USTA", "Universidad Santo Tomás", AN, ["Universidad Santo Tomas"]),
    ("U. Sergio Arboleda", "Universidad Sergio Arboleda", AN, ["Sergio Arboleda"]),
    ("U. de Medellín", "Universidad de Medellín", AN, ["Universidad de Medellin"]),
    ("Politécnico JIC", "Politécnico Colombiano Jaime Isaza Cadavid", AN, ["Politecnico Colombiano"]),
    ("ITM", "Institución Universitaria ITM", AN, ["Institucion Universitaria ITM"]),
    ("U. Distrital", "Universidad Distrital Francisco José de Caldas", AN, ["Universidad Distrital"]),
    ("UCM", "Universidad Católica de Manizales", AN, ["Universidad Catolica de Manizales"]),
    ("Uniautónoma", "Universidad Autónoma del Cauca", AN, ["Uniautonoma"]),
    ("UFPS Ocaña", "Universidad Francisco de Paula Santander Ocaña", AN, ["Francisco de Paula Santander"]),
    ("ESAP", "Escuela Superior de Administración Pública", AN, ["ESAP"]),
    ("UMB", "Universidad Manuela Beltrán", AN, ["Manuela Beltran"]),
    ("U. Quindío", "Universidad del Quindío", AN, ["Universidad del Quindio"]),
    ("UPTC", "Universidad Pedagógica y Tecnológica de Colombia", AN, ["=UPTC"]),
    ("U. Manizales", "Universidad de Manizales", AN, ["Universidad de Manizales"]),
    ("UDCA", "Universidad de Ciencias Aplicadas y Ambientales", AN, ["U.D.C.A", "=UDCA"]),
    ("ASCUN", "Asociación Colombiana de Universidades", AN, ["ASCUN"]),
    ("REDULAC", "Red Universitaria de América Latina y el Caribe para la RRD", AN, ["REDULAC"]),
    ("ETH Zurich", "Instituto Federal de Tecnología de Zúrich", AI, ["ETH"]),
    ("U. Barcelona", "Universidad de Barcelona", AI, ["Universidad de Barcelona"]),
    ("EPFL", "École Polytechnique Fédérale de Lausanne", AI, ["EPFL"]),
    ("U. Coimbra", "Universidad de Coimbra", AI, ["Universidad de Coimbra"]),
    ("ISTA", "Institute of Science and Technology Austria", AI, ["Institute of Science and Technology Austria"]),
    ("Yale", "Universidad de Yale", AI, ["Yale"]),
    ("La Salle México", "Universidad La Salle México", AI, ["La Salle Mexico"]),
    ("UNICI", "Universidad Internacional del Conocimiento e Investigación (México)", AI, ["UNICI"]),
    ("ENAPROC", "Escuela Nacional de Protección Civil (México)", AI, ["ENAPROC"]),
    ("AIS", "Asociación Colombiana de Ingeniería Sísmica", GR, ["=AIS", "Ingenieria Sismica"]),
    ("Fasecolda", "Federación de Aseguradores Colombianos", GR, ["Fasecolda"]),
    ("Consejo Colombiano de Seguridad", "Consejo Colombiano de Seguridad", GR, ["Consejo Colombiano de Seguridad"]),
    ("Responsabilidad Integral", "Responsabilidad Integral Colombia", GR, ["Responsabilidad Integral"]),
    ("ANDI", "Asociación Nacional de Empresarios de Colombia", GR, ["=ANDI"]),
    ("SCG", "Sociedad Colombiana de Geología", GR, ["Sociedad Colombiana de Geologia", "=SCG"]),
    ("ACGGP", "Asociación Colombiana de Geólogos y Geofísicos del Petróleo", GR, ["=ACGGP"]),
    ("OSSO", "Corporación OSSO", OT, ["OSSO"]),
    ("LIGA", "Liga Colombiana de Radioaficionados", OT, ["=LIGA", "Radioaficionados"]),
    ("Cenicafé", "Centro Nacional de Investigaciones de Café", OT, ["Cenicafe"]),
    ("CTA", "Corporación Centro de Ciencia y Tecnología de Antioquia", OT, ["Centro de Ciencia y Tecnologia de Antioquia", "=CTA"]),
    ("AstroCO", "Comunidad Colombiana de Astronomía", OT, ["AstroCO"]),
    ("OGC", "Observatorio Julio Garavito (Gimnasio Campestre)", OT, ["Observatorio Julio Garavito"]),
    ("RJRRD COL", "Red de Jóvenes para la Reducción del Riesgo de Desastres de Colombia", SC, ["RJRRD", "Red Nacional de Jovenes", "Red de Jovenes para la Reduccion"]),
    ("ORFE", "Observatorio de Riesgo, Fuego y Emergencias (ORFE)", SC, ["=ORFE"]),
    ("FUNSEMEVI", "FUNSEMEVI", SC, ["FUNSEMEVI"]),
    ("Nariño Joven", "Organización Nariño Joven", SC, ["Narino Joven"]),
    ("Fund. Almalina", "Fundación Almalina", SC, ["Almalina"]),
    ("Trendmakers", "Trendmakers Red Nacional del Agua", SC, ["Trendmakers"]),
    ("Presentes", "Presentes Corporación", SC, ["Presentes Corporacion"]),
    ("FGR", "Fundación para la Gestión del Riesgo", SC, ["Fundacion para la Gestion de Riesgos", "Fundacion para la Gestion del Riesgo", "=FGR"]),
    ("Proyecto ALA / HTM", "Proyecto ALA (Animales Latinoamérica) — Fundación HTM", SC, ["Proyecto ALA", "Fundacion HTM", "Grupo HTM"]),
    ("FUMSOL", "Fundación Mensajeros del Sol", SC, ["FUMSOL"]),
    ("AURORA", "AURORA Comunicaciones", SC, ["AURORA"]),
    ("Objetores", "Acción Colectiva de Objetores y Objetoras de Conciencia", SC, ["Objetores"]),
    ("MPC", "Mesa Permanente de Concertación — Organizaciones Indígenas Nacionales", SC, ["Mesa Permanente de Concertacion", "=ONIC", "=OPIAC", "=CRIC"]),
    ("JAC Tinajones", "Junta de Acción Comunal Isla Los Milagros Tinajones", SC, ["Junta de Accion Comunal"]),
    ("Aqualogs", "Aqualogs SAS", SP, ["Aqualogs"]),
    ("CIRMAC", "CIRMAC S.A.S.", SP, ["CIRMAC"]),
    ("IDOM", "IDOM — Consulting, Engineering and Architecture", SP, ["IDOM"]),
    ("Ingeniería Global", "Ingeniería Global y Servicios S.A.S.", SP, ["Ingenieria Global y Servicios"]),
    ("JOYCO", "JOYCO BIC SAS", SP, ["JOYCO"]),
    ("Yachiyo", "Yachiyo Engineering Co., Ltd.", SP, ["Yachiyo"]),
    ("Ecopetrol", "Ecopetrol", SP, ["Ecopetrol"]),
    ("Cenit", "Cenit Transporte y Logística de Hidrocarburos", SP, ["Cenit"]),
]

CASE_SENS = {"Yale", "Cenit", "ETH"}  # palabras cortas con riesgo de coincidir dentro de otras

ROL_ORDEN = ["Anfitriona", "Co-anfitriona", "Ponente", "Autoría"]


def plano(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def compilar():
    out = []
    for sigla, nombre, tipo, pats in REGISTRO:
        res = []
        for p in pats:
            if " " not in p and len(p.lstrip("=")) <= 9 and p.lstrip("=").upper() == p.lstrip("=") or p.startswith("=") or p in CASE_SENS:
                res.append(re.compile(r"(?<![\w])" + re.escape(p.lstrip("=")) + r"(?![\w])"))
            else:
                res.append(re.compile(re.escape(plano(p)), re.I))
        out.append((sigla, nombre, tipo, res))
    return out


def detectar(texto, comp):
    t = plano(texto)
    return {s for s, _, _, res in comp if any(r.search(t) for r in res)}


def leer_capitulos():
    caps = []
    for f in sorted(glob.glob(ROOT + "/*/*/index.qmd")):
        sec, slug = f.split("/")[-3:-1]
        if not re.match(r"^[a-z]+-\d+$", slug):
            continue
        t = open(f, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
        fm = yaml.safe_load(m.group(1)) if m else {}
        titulo = str(fm.get("title", slug))
        titulo = re.sub(r"^[^.]*\d+\.\s*", "", titulo) if re.match(r"^(Plenaria|Sesi|Laborat|Di[aá]logo|Escenario|P[oó]ster)[^.]*\d+\. ", titulo) else titulo
        fuentes = {"Anfitriona": [], "Co-anfitriona": [], "Ponente": [], "Autoría": []}
        for a in fm.get("author") or []:
            if isinstance(a, dict):
                for af in a.get("affiliations") or []:
                    fuentes["Autoría"].append(af.get("name", "") if isinstance(af, dict) else str(af))
        for k, v in re.findall(r"^\|\s*\*\*(Organizaci[^|*]*)\*\*\s*\|\s*(.*?)\s*\|\s*$", t, re.M):
            fuentes["Co-anfitriona" if "Co" in k else "Anfitriona"].append(v)
        m2 = re.search(r"^\|\s*(?:Conferencistas|Panelistas|Ponentes|Facilitadores)[^|]*\|\s*(.*?)\s*\|\s*$", t, re.M)
        if m2:
            fuentes["Ponente"].append(m2.group(1))
        caps.append(dict(sec=sec, slug=slug, titulo=titulo.strip(), href=f"{sec}/{slug}/index.qmd", fuentes=fuentes))
    return caps


def main():
    comp = compilar()
    meta = {s: (n, t) for s, n, t, _ in comp}
    base = {x["sigla"]: x for x in json.load(open(PREVIO, encoding="utf-8"))}
    caps = leer_capitulos()
    por_inst, huerfanos = {}, []
    for c in caps:
        roles = {}
        for rol in ROL_ORDEN:
            hallados = set()
            for txt in c["fuentes"][rol]:
                h = detectar(txt, comp)
                hallados |= h
                if not h and txt.strip() and plano(txt).lower() not in ("na", "no aplica"):
                    huerfanos.append((c["slug"], rol, txt[:110]))
            for s in hallados:
                roles.setdefault(s, rol)  # conserva el rol más alto
        for s, rol in roles.items():
            por_inst.setdefault(s, []).append(dict(sec=c["sec"], slug=c["slug"], titulo=c["titulo"], href=c["href"], rol=rol))
    if "--huerfanos" in sys.argv:
        for h in huerfanos:
            print(*h, sep=" | ")
        return
    res = []
    for sigla, nombre, tipo, _ in comp:
        b = base.get(sigla, {})
        if sigla not in por_inst and not b:
            continue
        res.append(dict(sigla=sigla, nombre=b.get("nombre", nombre), tipo=tipo,
                        color=COLOR[tipo], descripcion=b.get("descripcion", ""), trabajos=por_inst.get(sigla, [])))
    res.sort(key=lambda x: (ORDEN_TIPOS.index(x["tipo"]), -len(x["trabajos"]), x["sigla"]))
    json.dump(res, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sin = [s for s in base if s not in por_inst]
    assert all(s in meta for s in base), "falta en REGISTRO"
    print(f"{len(caps)} capítulos, {len(res)} instituciones, {sum(len(x['trabajos']) for x in res)} vínculos")
    print("De la lista original sin trabajos:", ", ".join(sin))


if __name__ == "__main__":
    main()
