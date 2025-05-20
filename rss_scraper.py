from argparse import ArgumentParser
from typing import List, Optional, Sequence
import requests
import xml.etree.ElementTree as ET

class UnhandledException(Exception):
    pass

def rss_parser(
    xml: str,
    limit: Optional[int] = None,
    json: bool = False,
) -> List[str]:
    """
    RSS parser.

    Args:
        xml: XML document as a string.
        limit: Number of the news to return. if None, returns all news.
        json: If True, format output as JSON.

    Returns:
        List of strings.
        Which then can be printed to stdout or written to file as a separate lines.

    Examples:
        xml = '<rss><channel><title>Some RSS Channel</title><link>https://some.rss.com</link><description>Some RSS Channel</description></channel></rss>'
        rss_parser(xml)
        ["Feed: Some RSS Channel",
        "Link: https://some.rss.com"]
        print("\\n".join(rss_parser(xmls)))
        Feed: Some RSS Channel
        Link: https://some.rss.com
    """
    try:
        root = ET.fromstring(xml)
        channel = root.find('channel')
        title = channel.find('title').text
        link = channel.find('link').text
        categories = channel.findall('category')
        cats = [cat.text for cat in categories if cat.text]
        items = channel.findall('item')
        if limit is not None:
            items = items[:limit]

        if json:
            import json
            json_output = {
                'title': title,
                'link': link,
                'description': channel.find('description').text if channel.find('description') is not None else "",
                'items': []
            }
            for item in items:
                item_dict = {
                    'title': item.find('title').text if item.find('title') is not None else "",
                    'pubDate': item.find('pubDate').text if item.find('pubDate') is not None else "",
                    'link': item.find('link').text if item.find('link') is not None else "",
                    'description': item.find('description').text if item.find('description') is not None else "",
                }
                json_output['items'].append(item_dict)
            return [json.dumps(json_output, indent=2, ensure_ascii=False)]

        output = [
            f"Feed: {title}",
            f"Link: {link}",
        ]
        if cats:
            output.append(f"Categories: {', '.join(cats)}")
        last_build_date = channel.find('lastBuildDate')
        if last_build_date is not None and last_build_date.text:
            output.append(f"Last Build Date: {last_build_date.text}")
        pub_date = channel.find('pubDate')
        if pub_date is not None and pub_date.text:
            output.append(f"Publish Date: {pub_date.text}")
        language = channel.find('language')
        if language is not None and language.text:
            output.append(f"Language: {language.text}")
        managing_editor = channel.find('managingEditor')
        if managing_editor is not None and managing_editor.text:
            output.append(f"Editor: {managing_editor.text}")
        description = channel.find('description')
        if description is not None and description.text:
            output.append(f"Description: {description.text}")

        for item in items:
            title_text = item.find('title').text if item.find('title') is not None else ''
            author = item.find('author').text if item.find('author') is not None else ''
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            categories = [cat.text for cat in item.findall('category') if cat.text]
            categories_text = ', '.join(categories)
            description = item.find('description').text if item.find('description') is not None else ''

            output.append(f"Title: {title_text}")
            if author:
                output.append(f"Author: {author}")
            if pub_date:
                output.append(f"Published: {pub_date}")
            if link:
                output.append(f"Link: {link}")
            if categories_text:
                output.append(f"Categories: {categories_text}")
            output.append('')
            output.append(f"Description: {description}")
            output.append("")

        return output
    except ET.ParseError as e:
        raise UnhandledException(e)

def main(argv: Optional[Sequence] = None):
    """
    The main function of your task.
    """
    parser = ArgumentParser(
        prog="rss_reader",
        description="Pure Python command-line RSS reader.",
    )
    parser.add_argument("source", help="RSS URL", type=str, nargs="?")
    parser.add_argument(
        "--json", help="Print result as JSON in stdout", action="store_true"
    )
    parser.add_argument(
        "--limit", help="Limit news topics if this parameter provided", type=int
    )

    args = parser.parse_args(argv)
    xml = requests.get(args.source).text
    try:
        print("\n".join(rss_parser(xml, args.limit, args.json)))
        return 0
    except Exception as e:
        raise UnhandledException(e)

if __name__ == "__main__":
    main()
