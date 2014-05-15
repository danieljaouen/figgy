# encoding: utf-8
# Created by David Rideout <drideout@safaribooksonline.com> on 2/7/14 4:58 PM
# Copyright (c) 2013 Safari Books Online, LLC. All rights reserved.

import django.core.exceptions
import storage.models
from storage.models import Alias, Book, Version


def get_aliases(book_element):
    aliases = []

    for alias in book_element.xpath('aliases/alias'):
        scheme = alias.get('scheme')
        value = alias.get('value')

        aliases.append(
            {
                'scheme': alias.get('scheme'),
                'value': alias.get('value'),
            }
        )

    return aliases


def get_or_create_book(book_element):
    # always get book by ISBN aliases
    aliases = get_aliases(book_element)

    found_alias = None
    for alias in aliases:
        try:
            found_alias = Alias.objects.get(
                scheme=alias['scheme'],
                value=alias['value'],
            )
        except django.core.exceptions.ObjectDoesNotExist:
            continue
        else:
            break

    if found_alias:
        return found_alias.book
    else:
        book = Book(id=book_element.get('id'))
        for alias in aliases:
            book.aliases.create(
                scheme=alias['scheme'],
                value=alias['value'],
            )
        book.save()
        return book


def process_book_element(book_element):
    """
    Process a book element into the database.

    :param book: book element
    :returns:
    """

    book = get_or_create_book(book_element)

    book.versions.get_or_create(
        version=book_element.findtext('version'),
        title=book_element.findtext('title'),
        description=book_element.findtext('description'),
    )

    book.save()
