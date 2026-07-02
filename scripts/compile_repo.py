import os
import re
import json
import yaml
import zipfile
from pathlib import Path

# Paths Setup
WORKSPACE_DIR = Path(__file__).parent.parent.parent.resolve()  # c:\AI\Agency owner
AETHERIS_DIR = WORKSPACE_DIR / "aetheris"
WEB_DIR = AETHERIS_DIR / "web"
PUBLIC_DIR = WEB_DIR / "public"
CONTENT_DIR = PUBLIC_DIR / "content"
DOWNLOADS_DIR = PUBLIC_DIR / "downloads" / "skills"

def ensure_dirs():
    """Ensure output directories exist."""
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    (CONTENT_DIR / "rfcs").mkdir(parents=True, exist_ok=True)
    (CONTENT_DIR / "specs").mkdir(parents=True, exist_ok=True)
    (CONTENT_DIR / "docs").mkdir(parents=True, exist_ok=True)
    (CONTENT_DIR / "skills").mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

def slugify(text):
    """Simple slugify helper."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text).strip("-")

def parse_markdown_sections(content):
    """
    Parse a markdown string into sections based on H2 headers (##).
    """
    sections = {}
    current_header = "Introduction"
    current_lines = []
    
    for line in content.split("\n"):
        if line.startswith("## "):
            sections[current_header] = "\n".join(current_lines).strip()
            current_header = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
            
    sections[current_header] = "\n".join(current_lines).strip()
    return sections

def extract_references(text):
    """
    Find references to RFCs, SPECs, and skill IDs.
    """
    rfcs = sorted(list(set(re.findall(r"\bRFC-\d{3}\b", text, re.IGNORECASE))))
    specs = sorted(list(set(re.findall(r"\bSPEC-\d{3}\b", text, re.IGNORECASE))))
    
    # Normalize casings
    rfcs = [r.upper() for r in rfcs]
    specs = [s.upper() for s in specs]
    
    return rfcs, specs

def parse_skills():
    """
    Scan for agency skills in division directories and core skills in aetheris/skills.
    """
    skills_registry = {}
    
    # 1. Load active divisions
    divisions_file = WORKSPACE_DIR / "divisions.json"
    divisions_meta = {}
    if divisions_file.exists():
        with open(divisions_file, "r", encoding="utf-8") as f:
            divisions_meta = json.load(f).get("divisions", {})
            
    # 2. Scan Division folders for Agency Skills
    for div_id, div_info in divisions_meta.items():
        div_dir = WORKSPACE_DIR / div_id
        if not div_dir.exists():
            continue
            
        for file in div_dir.glob("*.md"):
            if file.name.lower() in ["readme.md", "skill.md"]:
                continue
                
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    
                # Extract frontmatter
                frontmatter = {}
                body = text
                if text.startswith("---"):
                    parts = text.split("---")
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        body = "---".join(parts[2:])
                        
                skill_id = file.stem
                name = frontmatter.get("name", skill_id.replace("agency-", "").replace("-", " ").title())
                description = frontmatter.get("description", "No description provided.")
                color = frontmatter.get("color", div_info.get("color", "#6366F1"))
                emoji = frontmatter.get("emoji", "🤖")
                vibe = frontmatter.get("vibe", "")
                
                # Parse sections
                sections = parse_markdown_sections(body)
                ref_rfcs, ref_specs = extract_references(body)
                
                # Infer inputs/outputs/benchmarks from common section headers
                inputs = ""
                outputs = ""
                examples = ""
                benchmarks = ""
                
                for title, sec_content in sections.items():
                    title_l = title.lower()
                    if "input" in title_l:
                        inputs = sec_content
                    elif "output" in title_l or "deliverable" in title_l:
                        outputs = sec_content
                    elif "example" in title_l or "template" in title_l:
                        examples = sec_content
                    elif "benchmark" in title_l or "success" in title_l:
                        benchmarks = sec_content
                
                skills_registry[skill_id] = {
                    "id": skill_id,
                    "type": "agency",
                    "name": name,
                    "description": description,
                    "version": frontmatter.get("version", "2.1.0"),
                    "author": frontmatter.get("author", "Aetheris Core"),
                    "division": div_id,
                    "division_label": div_info.get("label", div_id.title()),
                    "color": color,
                    "emoji": emoji,
                    "vibe": vibe,
                    "tags": frontmatter.get("tags", [div_id, "agency-agent"]),
                    "inputs": inputs or "Read workspace context, analyze requirements, execute sub-tasks.",
                    "outputs": outputs or "Code modifications, verification reports, decision logs.",
                    "examples": examples or "N/A",
                    "benchmarks": benchmarks or "N/A",
                    "related_rfcs": ref_rfcs,
                    "related_specs": ref_specs,
                    "file_path": str(file.relative_to(WORKSPACE_DIR)).replace("\\", "/")
                }
                
                # Save markdown file to public content directory
                with open(CONTENT_DIR / "skills" / f"{skill_id}.md", "w", encoding="utf-8") as out:
                    out.write(text)
                    
            except Exception as e:
                print(f"Error parsing skill file {file}: {e}")
                
    # 3. Scan Core Skills in aetheris/skills
    core_skills_dir = AETHERIS_DIR / "skills"
    if core_skills_dir.exists():
        for skill_dir in core_skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
                
            try:
                with open(skill_file, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    
                frontmatter = {}
                body = text
                if text.startswith("---"):
                    parts = text.split("---")
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        body = "---".join(parts[2:])
                        
                skill_id = skill_dir.name
                name = frontmatter.get("name", skill_id.replace("aetheris-", "").replace("-", " ").title())
                description = frontmatter.get("description", "Aetheris kernel capability engine.")
                ref_rfcs, ref_specs = extract_references(body)
                
                skills_registry[skill_id] = {
                    "id": skill_id,
                    "type": "core",
                    "name": name,
                    "description": description,
                    "version": frontmatter.get("metadata", {}).get("version", "3.0.0"),
                    "author": "Aetheris Kernel Team",
                    "division": "core",
                    "division_label": "Kernel Core",
                    "color": "#3B82F6",
                    "emoji": "🧠",
                    "vibe": "Runs inside the secure Aetheris execution loop.",
                    "tags": ["kernel", "core", "engine"],
                    "inputs": "Goal definition, DAG specifications, raw repository files.",
                    "outputs": "Execution state, compiled context, verified results.",
                    "examples": "N/A",
                    "benchmarks": "Verified zero-leak execution context.",
                    "related_rfcs": ref_rfcs,
                    "related_specs": ref_specs,
                    "file_path": str(skill_file.relative_to(WORKSPACE_DIR)).replace("\\", "/")
                }
                
                with open(CONTENT_DIR / "skills" / f"{skill_id}.md", "w", encoding="utf-8") as out:
                    out.write(text)
                    
            except Exception as e:
                print(f"Error parsing core skill {skill_file}: {e}")
                
    return skills_registry

def parse_rfcs_and_specs():
    """
    Parse RFC and SPEC files from aetheris/rfcs.
    """
    rfcs = {}
    specs = {}
    
    rfcs_dir = AETHERIS_DIR / "rfcs"
    if not rfcs_dir.exists():
        return rfcs, specs
        
    for file in rfcs_dir.glob("*.md"):
        try:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            # Scan title from first header
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else file.stem
            
            ref_rfcs, ref_specs = extract_references(content)
            
            # Find ID
            rfc_match = re.match(r"^(RFC-\d{3})", file.name, re.IGNORECASE)
            spec_match = re.match(r"^(SPEC-\d{3})", file.name, re.IGNORECASE)
            
            if rfc_match:
                rfc_id = rfc_match.group(1).upper()
                rfcs[rfc_id] = {
                    "id": rfc_id,
                    "title": title,
                    "filename": file.name,
                    "related_rfcs": [r for r in ref_rfcs if r != rfc_id],
                    "related_specs": ref_specs,
                    "file_path": str(file.relative_to(WORKSPACE_DIR)).replace("\\", "/")
                }
                # Copy to public content
                with open(CONTENT_DIR / "rfcs" / file.name, "w", encoding="utf-8") as out:
                    out.write(content)
                    
            elif spec_match:
                spec_id = spec_match.group(1).upper()
                
                # Parse specific section summaries for SPECs
                sections = parse_markdown_sections(content)
                goals = sections.get("Goals", "") or sections.get("Purpose", "")
                inputs = sections.get("Inputs", "")
                outputs = sections.get("Outputs", "")
                definition_of_done = sections.get("Definition of Done", "")
                
                specs[spec_id] = {
                    "id": spec_id,
                    "title": title,
                    "filename": file.name,
                    "goals": goals[:300] + "..." if len(goals) > 300 else goals,
                    "inputs": inputs[:300] + "..." if len(inputs) > 300 else inputs,
                    "outputs": outputs[:300] + "..." if len(outputs) > 300 else outputs,
                    "dod": definition_of_done[:300] + "..." if len(definition_of_done) > 300 else definition_of_done,
                    "related_rfcs": ref_rfcs,
                    "related_specs": [s for s in ref_specs if s != spec_id],
                    "file_path": str(file.relative_to(WORKSPACE_DIR)).replace("\\", "/")
                }
                # Copy to public content
                with open(CONTENT_DIR / "specs" / file.name, "w", encoding="utf-8") as out:
                    out.write(content)
                    
        except Exception as e:
            print(f"Error parsing RFC/SPEC file {file}: {e}")
            
    return rfcs, specs

def parse_docs():
    """
    Parse docs and ADRs.
    """
    docs = {}
    
    # 1. Scan aetheris/docs/
    docs_dir = AETHERIS_DIR / "docs"
    if docs_dir.exists():
        for file in docs_dir.glob("*.md"):
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else file.stem
                doc_id = file.stem
                
                ref_rfcs, ref_specs = extract_references(content)
                
                docs[doc_id] = {
                    "id": doc_id,
                    "title": title,
                    "type": "guide",
                    "filename": file.name,
                    "related_rfcs": ref_rfcs,
                    "related_specs": ref_specs,
                    "file_path": str(file.relative_to(WORKSPACE_DIR)).replace("\\", "/")
                }
                # Copy to public content
                with open(CONTENT_DIR / "docs" / file.name, "w", encoding="utf-8") as out:
                    out.write(content)
            except Exception as e:
                print(f"Error parsing doc {file}: {e}")
                
    # 2. Scan aetheris/adrs/
    adrs_dir = AETHERIS_DIR / "adrs"
    if adrs_dir.exists():
        for file in adrs_dir.glob("*.md"):
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else file.stem
                doc_id = file.stem
                
                ref_rfcs, ref_specs = extract_references(content)
                
                docs[doc_id] = {
                    "id": doc_id,
                    "title": title,
                    "type": "adr",
                    "filename": file.name,
                    "related_rfcs": ref_rfcs,
                    "related_specs": ref_specs,
                    "file_path": str(file.relative_to(WORKSPACE_DIR)).replace("\\", "/")
                }
                # Copy to public content
                with open(CONTENT_DIR / "docs" / file.name, "w", encoding="utf-8") as out:
                    out.write(content)
            except Exception as e:
                print(f"Error parsing ADR {file}: {e}")
                
    return docs

def build_search_index(skills, rfcs, specs, docs):
    """
    Create a clean search index for client-side TF-IDF matches.
    """
    search_index = []
    
    # 1. Add skills
    for skill_id, skill in skills.items():
        content_block = f"{skill['name']} {skill['description']} {skill['division_label']} {skill['inputs']} {skill['outputs']}"
        search_index.append({
            "id": f"skills/{skill_id}",
            "title": skill["name"],
            "subtitle": f"{skill['division_label']} Skill",
            "type": "skill",
            "tags": skill["tags"],
            "content": content_block.lower()
        })
        
    # 2. Add RFCs
    for rfc_id, rfc in rfcs.items():
        search_index.append({
            "id": f"rfcs/{rfc_id}",
            "title": rfc_id,
            "subtitle": rfc["title"],
            "type": "rfc",
            "tags": ["rfc", "architecture"],
            "content": f"{rfc_id} {rfc['title']}".lower()
        })
        
    # 3. Add SPECs
    for spec_id, spec in specs.items():
        content_block = f"{spec_id} {spec['title']} {spec['goals']} {spec['inputs']} {spec['outputs']}"
        search_index.append({
            "id": f"specs/{spec_id}",
            "title": spec_id,
            "subtitle": spec["title"],
            "type": "spec",
            "tags": ["spec", "specification", "implementation"],
            "content": content_block.lower()
        })
        
    # 4. Add Docs
    for doc_id, doc in docs.items():
        search_index.append({
            "id": f"docs/{doc_id}",
            "title": doc["title"],
            "subtitle": "System Documentation" if doc["type"] == "guide" else "Architecture Decision Record",
            "type": "doc",
            "tags": [doc["type"], "documentation"],
            "content": f"{doc['title']} {doc_id}".lower()
        })
        
    return search_index

def generate_downloads(skills):
    """
    Create dynamic downloads (Markdown, JSON, YAML, and ZIP) for each skill.
    """
    for skill_id, skill in skills.items():
        skill_dl_dir = DOWNLOADS_DIR / skill_id
        skill_dl_dir.mkdir(parents=True, exist_ok=True)
        
        # Read source markdown
        src_path = WORKSPACE_DIR / skill["file_path"]
        if not src_path.exists():
            continue
            
        with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
            md_content = f.read()
            
        # 1. Save MD
        md_file = skill_dl_dir / f"{skill_id}.md"
        with open(md_file, "w", encoding="utf-8") as out:
            out.write(md_content)
            
        # 2. Save JSON
        json_file = skill_dl_dir / f"{skill_id}.json"
        with open(json_file, "w", encoding="utf-8") as out:
            json.dump(skill, out, indent=2)
            
        # 3. Save YAML
        yaml_file = skill_dl_dir / f"{skill_id}.yaml"
        # Separate frontmatter and body
        yaml_content = yaml.dump(skill, default_flow_style=False)
        with open(yaml_file, "w", encoding="utf-8") as out:
            out.write(yaml_content)
            
        # 4. Save ZIP
        zip_file = skill_dl_dir / f"{skill_id}.zip"
        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zip_h:
            zip_h.write(md_file, arcname=f"{skill_id}.md")
            zip_h.write(json_file, arcname=f"{skill_id}.json")
            zip_h.write(yaml_file, arcname=f"{skill_id}.yaml")

def build_graph_data(skills, rfcs, specs):
    """
    Generate dependency nodes and links for the architecture graph visualization.
    """
    nodes = []
    links = []
    
    # Helper to add node if not exists
    added_nodes = set()
    def add_node(node_id, label, type_name, color):
        if node_id not in added_nodes:
            nodes.append({
                "id": node_id,
                "label": label,
                "type": type_name,
                "color": color
            })
            added_nodes.add(node_id)
            
    # 1. Add RFCs
    for rfc_id, rfc in rfcs.items():
        add_node(rfc_id, f"{rfc_id}: {rfc['title']}", "rfc", "#8B5CF6")
        
    # 2. Add SPECs
    for spec_id, spec in specs.items():
        add_node(spec_id, f"{spec_id}: {spec['title']}", "spec", "#EC4899")
        # Link SPEC ➔ RFC
        for rfc in spec["related_rfcs"]:
            if rfc in rfcs:
                links.append({"source": spec_id, "target": rfc, "type": "spec_rfc"})
        # Link SPEC ➔ SPEC
        for s in spec["related_specs"]:
            if s in specs:
                links.append({"source": spec_id, "target": s, "type": "spec_spec"})
                
    # 3. Add Skills
    for skill_id, skill in skills.items():
        add_node(skill_id, skill["name"], "skill", skill["color"])
        # Link Skill ➔ RFC
        for rfc in skill["related_rfcs"]:
            if rfc in rfcs:
                links.append({"source": skill_id, "target": rfc, "type": "skill_rfc"})
        # Link Skill ➔ SPEC
        for spec in skill["related_specs"]:
            if spec in specs:
                links.append({"source": skill_id, "target": spec, "type": "skill_spec"})
                
    return {"nodes": nodes, "links": links}

def main():
    print("Starting Aetheris Repository Scanner & Compiler...")
    ensure_dirs()
    
    skills = parse_skills()
    print(f"Scanned {len(skills)} skills successfully.")
    
    rfcs, specs = parse_rfcs_and_specs()
    print(f"Scanned {len(rfcs)} RFCs and {len(specs)} SPECs successfully.")
    
    docs = parse_docs()
    print(f"Scanned {len(docs)} documents/ADRs successfully.")
    
    search_index = build_search_index(skills, rfcs, specs, docs)
    print(f"Built full-text search index containing {len(search_index)} documents.")
    
    graph_data = build_graph_data(skills, rfcs, specs)
    print(f"Generated architecture graph data with {len(graph_data['nodes'])} nodes.")
    
    print("Generating skill download packages (ZIP, YAML, JSON, MD)...")
    generate_downloads(skills)
    
    # Save the consolidated database
    db_file = PUBLIC_DIR / "data.json"
    db_data = {
        "skills": skills,
        "rfcs": rfcs,
        "specs": specs,
        "docs": docs,
        "search_index": search_index,
        "graph": graph_data
    }
    
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(db_data, f, indent=2)
        
    print(f"SUCCESS: Compiled repository-driven database saved to {db_file}")

if __name__ == "__main__":
    main()
