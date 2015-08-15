#!/usr/bin/env python2
import os
import os.path
import sqlite3

class PhraseDB(object):
    def __init__(self, dbpath, new=False):
        self.new = new

        if new:
            if os.path.exists(dbpath):
                if raw_input('Phrase database already exists! Override [y/N]? ') == 'y':
                    os.remove(dbpath)
                else:
                    self.new = False
        else:
            if not os.path.exists(dbpath):
                raise ValueError()

        self.conn = sqlite3.connect(dbpath)
        if self.new:
            self.create_db()

        self.conn.commit()
        cur = self.conn.cursor()
        cur.execute('PRAGMA synchronous = OFF')

    @staticmethod
    def canonicalize(phrase):
        return u';'.join(phrase)

    @staticmethod
    def uncanonicalize(phrase):
        return tuple(phrase.split(';'))

    @property
    def phrase_pairs_available(self):
        cur = self.conn.cursor()
        cur.execute('SELECT val FROM properties WHERE key=\'pairs_available\'')
        return bool(cur.fetchone()[0])

    @phrase_pairs_available.setter
    def update_phrase_pairs_available(self, val):
        cur = self.conn.cursor()
        cur.execute('UPDATE properties SET val=? WHERE key=\'pairs_available\'', int(val))

    @property
    def trans_probs_available(self):
        cur = self.conn.cursor()
        cur.execute('SELECT val FROM properties WHERE key=\'probs_available\'')
        return bool(cur.fetchone()[0])

    @trans_probs_available.setter
    def update_trans_probs_available(self, val):
        cur = self.conn.cursor()
        cur.execute('UPDATE properties SET val=? WHERE key=\'probs_available\'', int(val))

    def create_db(self):
        cur = self.conn.cursor()
        cur.execute('CREATE TABLE phrase_pairs(src TEXT, dst TEXT)')
        cur.execute('CREATE TABLE phrase_pairs_probs(src TEXT, dst TEXT, prob REAL)')
        cur.execute('CREATE TABLE properties(key TEXT, val INTEGER)')
        cur.execute('INSERT INTO properties VALUES(\'pairs_available\', 0)')
        cur.execute('INSERT INTO properties VALUES(\'probs_available\', 0)')

    def cursor(self):
        return self.conn.cursor()

    def create_probs_index(self):
        cur = self.conn.cursor()
        cur.execute('CREATE INDEX IF NOT EXISTS phrase_probs_by_src ON phrase_pairs_probs(src)')
        self.conn.commit()

    def add_phrase_pairs(self, pairs):
        cur = self.conn.cursor()
        for pair in pairs:
            src = PhraseDB.canonicalize(pair[0])
            dst = PhraseDB.canonicalize(pair[1])
            cur.execute('INSERT INTO phrase_pairs VALUES(?, ?)', (src,dst))
        self.conn.commit()

    def add_trans_probs(self, trans_probs):
        cur = self.conn.cursor()
        for row in trans_probs:
            cur.execute('INSERT INTO phrase_pairs_probs VALUES(?, ?, ?)', row)
        self.conn.commit()

    def mark_trans_probs_completed(self):
        cur = self.conn.cursor()
        cur.execute('UPDATE properties SET val=1 WHERE key=\'probs_available\'')

    def phrases(self):
        cur = self.conn.cursor()
        cur.execute('SELECT *, COUNT(*) as count FROM phrase_pairs GROUP BY src, dst')
        for row in cur:
            yield row

    def phrases_count(self):
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(*) FROM phrase_pairs')
        return cur.fetchone()[0]

    def dst_phrases(self):
        cur = self.conn.cursor()
        cur.execute('SELECT dst, COUNT(src) FROM phrase_pairs GROUP BY dst')
        for row in cur:
            yield row

    def dst_phrases_count(self):
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(*) FROM (SELECT DISTINCT dst FROM phrase_pairs) AS tmp')
        return cur.fetchone()[0]

    def get_translations(self, phrase):
        cur = self.conn.cursor()
        cur.execute('SELECT dst, prob FROM phrase_pairs_probs WHERE src=?',
                (PhraseDB.canonicalize(phrase),))
        for trans, prob in cur:
            yield (phrase, PhraseDB.uncanonicalize(trans), prob)

    def close(self):
        self.conn.close()
