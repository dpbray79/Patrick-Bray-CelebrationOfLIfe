import re
import json

with open('index.html', 'r') as f:
    html = f.read()

with open('expanded_data.js', 'r') as f:
    js = f.read()

with open('patrick_bray_slideshow_workplan.html', 'r') as f:
    workplan = f.read()

# Extract chapter labels and summaries
chapter_match = re.search(r'const chapterLabels = (\{.*?\});', html, re.DOTALL)
chapters = {}
if chapter_match:
    try:
        # Regex to pull out the keys and label/summary pairs
        ch_blocks = re.findall(r'"(.*?)":\s*\{\s*label:\s*"(.*?)",\s*summary:\s*"(.*?)"\s*}', chapter_match.group(1), re.DOTALL)
        for orig_name, label, summary in ch_blocks:
            chapters[orig_name] = {'label': label, 'summary': summary}
    except:
        pass

# Extract expanded data properly
expanded = {}
json_str = re.search(r'const expandedNarratives = (\{.*?\});\s*window', js, re.DOTALL)
if json_str:
    try:
        expanded = json.loads(json_str.group(1))
    except Exception as e:
        print("JSON parse failed", e)

output = []
output.append("# Patrick Weldon Bray - Celebration of Life\n")
output.append("## Master Presentation Reference Guide\n\n")

output.append("### Landing Page (Cover)\n")
output.append("- **Photo**: `cover_photo.jpg` (Headshot)\n")
output.append("- **Text**: Remembering Patrick Weldon Bray | November 17th, 1932 — April 28th, 2026\n")
output.append("- **Action**: 'Begin Celebration' button initiates the automated slideshow.\n\n")

output.append("### Slide 0: Opening Tribute\n")
output.append(f"- **Chapter Intro**: {chapters.get('Opening', {}).get('label')}\n")
output.append(f"- **Summary Text**: {chapters.get('Opening', {}).get('summary')}\n\n")

from html.parser import HTMLParser

class WorkplanParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_chapter_name = False
        self.in_td = False
        self.current_chapter = ""
        self.current_td_index = 0
        self.current_row_data = []
        
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div' and attrs.get('class') == 'chapter-name':
            self.in_chapter_name = True
        elif tag == 'tr':
            self.current_row_data = []
            self.current_td_index = 0
        elif tag == 'td':
            self.in_td = True
            self.current_row_data.append("")

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_chapter_name:
            self.in_chapter_name = False
            raw_name = self.current_chapter.strip()
            ch_data = chapters.get(raw_name, {'label': raw_name.upper(), 'summary': ''})
            output.append(f"---\n\n## CHAPTER: {ch_data['label']}\n")
            if ch_data['summary']:
                output.append(f"**Chapter Introduction Screen:**\n> {ch_data['summary']}\n\n")
            self.current_chapter = ""
            
        elif tag == 'tr':
            if len(self.current_row_data) >= 5:
                num = self.current_row_data[0].strip()
                if not num.isdigit():
                    pass
                else:
                    orig_title = self.current_row_data[1].strip()
                    orig_story = self.current_row_data[3].strip()
                    photo_cell = self.current_row_data[4]
                    
                    final_data = expanded.get(num, {})
                    title = final_data.get('title', orig_title)
                    subtitle = final_data.get('subtitle', 'Patrick Weldon Bray')
                    story = final_data.get('story', orig_story)
                    
                    images = []
                    if 'images' in final_data:
                        images = final_data['images']
                    elif num == "1":
                        images = ["port_morien_sign.jpg", "port_morien_map.jpg"]
                    else:
                        images = re.findall(r'image\d+\.(?:jpg|png|jpeg)', photo_cell, re.IGNORECASE)
                        
                    output.append(f"### Slide {num}\n")
                    output.append(f"- **Title**: {title}\n")
                    output.append(f"- **Subtitle**: {subtitle}\n")
                    output.append(f"- **Narrative**: {story}\n")
                    if images:
                        output.append(f"- **Photos**: {', '.join(images)}\n")
                    else:
                        output.append(f"- **Photos**: None\n")
                    output.append("\n")
                    
        elif tag == 'td':
            self.in_td = False
            self.current_td_index += 1

    def handle_data(self, data):
        if self.in_chapter_name:
            self.current_chapter += data
        elif self.in_td:
            self.current_row_data[self.current_td_index] += data

parser = WorkplanParser()
parser.feed(workplan)

with open('Presentation_Reference_Guide.md', 'w') as f:
    f.write(''.join(output))

print("Fixed Guide generated successfully.")
