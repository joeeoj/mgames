#!/usr/bin/env python3
"""Simple CLI to get the Mariners schedule from the MLB API. Can extend to other teams and venues."""
import argparse
import csv
import json
from typing import List

import arrow
import requests


TEAM_ID = 136  # M's
VENUE_ID = 680  # t-mobile park
LOCAL_TZ = 'US/Pacific'

BASE_QUERY = f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={TEAM_ID}&startDate={{start}}&endDate={{end}}'


def parse_date(s: str) -> str:
    """parse given date string into date format and return as MM/DD/YYYY str per statsapi specs"""
    return arrow.get(s).format('MM/DD/YYYY')


def parse_response(resp: dict) -> dict:
    """Trim down full response"""
    games, i = [], 0
    for row in resp.get('dates'):
        for game in row.get('games'):
            i += 1
            d = {}

            d['game_number'] = i
            d['game_date'] = row.get('date')

            game_date = arrow.get(game.get('gameDate')).to(LOCAL_TZ)
            d['day_of_week'] = game_date.format('ddd')
            d['game_time_local'] = game_date.format('hh:mm A')

            d['is_home_game'] = int(game.get('venue').get('id') == VENUE_ID)
            d['venue'] = game.get('venue').get('name')
            d['series_number'] = game.get('seriesGameNumber')
            d['day_night'] = game.get('dayNight')

            teams = game.get('teams')
            d['home'] = teams.get('home').get('team').get('name')
            d['away'] = teams.get('away').get('team').get('name')

            games.append(d)

    return {
        'current_datetime': arrow.utcnow().to(LOCAL_TZ).format(),
        'total_games': resp.get('totalGames'),
        'in_progress': resp.get('totalGamesInProgress'),
        'games': games
    }


def get_data(start: str, end: str) -> dict:
    """Get data from statsapi and trim down"""
    r = requests.get(BASE_QUERY.format(start=parse_date(start), end=parse_date(end)))
    if r.status_code != 200:
        return None
    return parse_response(r.json())


def write_to_csv(fout: str, games: List[dict]) -> None:
    """Write list of games to csv"""
    with open(fout, 'wt') as f:
        csvwriter = csv.DictWriter(f, fieldnames=games[0].keys())
        csvwriter.writeheader()
        csvwriter.writerows(games)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='mgames', description='Query MLB API to get Mariners schedule from given date range')
    parser.add_argument('start', help='Search start date (most formats should work)')
    parser.add_argument('end', help='Search end date')
    parser.add_argument('--fout', help='Export result to csv')
    parser.add_argument('--home-only', help='Show only home games', action='store_true')
    args = parser.parse_args()

    data = get_data(args.start, args.end)
    games = data.get('games')

    # add home game number count
    i = 1
    for game in games:
        if game.get('is_home_game'):
            game['home_game_number'] = i
            i += 1
        else:
            game['home_game_number'] = None

    print(f'Total games found: {data.get("total_games"):,}')
    print(f'Games in progress: {data.get("in_progress"):,}')

    if args.home_only:
        games = [g for g in games if g['is_home_game']]
        print(f' Total home games: {len(games):,}')

    if args.fout:
        write_to_csv(args.fout, games)
    else:
        for game in games:
            print(json.dumps(game, indent=2))
