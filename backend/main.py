from scraper import scrape_links, scrape_content


def main():

    # Step 1: Scrape links from guidelines page
    links: list[str] = scrape_links()

    # Step 2: for each link, scrape relevant content from the page, requires different strategy
    # per website
    # content: list[str] = scrape_content(links)


if __name__ == "__main__":
    main()
