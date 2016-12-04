#!/usr/bin/env python3

import flickrapi
import configparser
import argparse

__author__ = 'kropp'

def main():
    parser = argparse.ArgumentParser(description='Generate fotorama.io gallery from Flickr photoset')
    parser.add_argument('--api-key', type=str, dest='api_key', help='Flickr API key')
    parser.add_argument('--api-secret', type=str, dest='api_secret', help='Flickr API secret')

    subparsers = parser.add_subparsers(dest='command')
    gallery_subparser = subparsers.add_parser('gallery', help='Generate fotorama.io gallery')
    gallery_subparser.add_argument('-s', '--set', type=str, required=True, dest='id', help='Flickr photoset id')

    album_subparser = subparsers.add_parser('albums', help='Print all user albums ids & titles')
    album_subparser.add_argument('-u', '--user', type=str, dest='user', help='Flickr user id')

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = args.api_key
    if not api_key:
        api_key = config.get('flickr', 'api_key')

    api_secret = args.api_secret
    if not api_secret:
        api_secret = config.get('flickr', 'api_secret')

    if not api_key or not api_secret:
        print("Please provide Flickr API key & secret")
        exit(1)

    flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

    if args.command == 'albums':
        user_id = args.user
        if not user_id:
            user_id = config.get('default', 'user')

        albums(flickr, user_id)
    elif args.command == 'gallery':
        gallery(flickr, args.id)
    else:
        print("Unknown command: " + args.command)
        exit(1)


def albums(flickr, user_id):
    sets = flickr.photosets.getList(user_id=user_id)
    for album in sets['photosets']['photoset']:
        print("{}: {}".format(album['id'], album['title']['_content']))


def getSize(sizes, name):
    all_sizes = sizes['sizes']['size']
    for size in all_sizes:
        if size['label'] == name:
            return size
    return all_sizes[len(all_sizes) - 1]


def gallery(flickr, album_id):
    photos_with_links = ""

    print('<div class="fotorama" data-allow-full-screen="native" data-keyboard="true" data-loop="true" data-width="100%">')
    for photo in flickr.photosets.getPhotos(photoset_id=album_id)['photoset']['photo']:
        sizes = flickr.photos.getSizes(photo_id=photo['id'])
        print('  <img src="' + getSize(sizes, 'Large 1600')['source'] + '" data-full="' + getSize(sizes, 'Original')[
            'source'] + '" data-caption="" />')
        photos_with_links += '<a href="' + getSize(sizes, 'Original')['source'] + '"><img src="' + \
                             getSize(sizes, 'Large 1600')['source'] + '" /></a>\n'

    print('</div>\n')

    print(photos_with_links)

if __name__ == '__main__':
    main()