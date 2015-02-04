from umls.models import MRCONSO
from umls.models import MRREL

from umls.utils import get_cui
from umls.utils import get_code
from django.db.models import Q
from django.db import connection


class CodeResource:
    """ The Terminology Code resource """

    def _get(self, vocab, code_val):
        terms = MRCONSO.objects.filter(SAB=vocab, CODE=code_val)
        rterms = []
        for term in terms:
            rterms.append({
                'term':term.SAB,
                'code':term.CODE,
                'name':term.STR,
                'umls_cui':term.CUI,
                #'is_preferred':term.ISPERF
            })

        return rterms

    def _get_code(self, code, sab):

        if sab:
            sablist = sab.split(',')
            print sab
            print 'sablist' + sab
            terms = MRCONSO.objects.filter(CODE=code).filter(SAB__in=sablist)
        else:
            terms = MRCONSO.objects.filter(CODE=code)

        rterms = []

        for term in terms:
            rterms.append({
                'code':term.CODE,
                'sab':term.SAB,
                'cuis':term.CUI,
                'str':term.STR,
            })

        return rterms

    def _get_code_det(self, code, sab):

        terms = MRCONSO.objects.filter(CODE=code, SAB=sab)

        rterms = []

        for term in terms:
            rterms.append({
                'code':term.CODE,
                'sab':term.SAB,
                'cuis':term.CUI,
                'str':term.STR,
            })

        return rterms


class RelResource:
    """ The Terminology Relationship resource """

    def _get(self, vocab, code_val, rel_type):

        source_cui = get_cui(vocab, code_val)
   
        rels_list = []
        if source_cui:
            rels = MRREL.objects.filter(CUI1=source_cui, RELA=rel_type)
            for rel in rels:
                rels_list.append({
                    'umls_cui':rel.CUI2,
                    'code':get_code(rel.SAB, rel.CUI2),
                    'rel':rel.REL,
                    'rela':rel.RELA
                })

        return rels_list

class MapResource:
    """ The Terminology Mapping resource """

    def _get(self, source_vocab, code_val, target_vocab):

        cui = get_cui(source_vocab, code_val)

        print cui
        terms = MRCONSO.objects.filter(CUI=cui, SAB=target_vocab)
        rterms = []
        for term in terms:
            rterms.append({
                'target_vocab':term.SAB,
                'code':term.CODE,
                'name':term.STR,
            })

        return rterms

class ConceptResource:
    """ The Terminology Code resource """

    def _get(self, cui):
        terms = MRCONSO.objects.filter(CUI=cui)
        rterms = []
        STR_list=[]
        SAB_list=[]
        for term in terms:
            STR_list.append(term.STR)
            SAB_list.append(term.SAB)
        rterms.append({
            'concept':cui,
            'terms':STR_list,
            'sabs':SAB_list,
        })

        return rterms

    def _get_term(self, str, sab):

        if sab:
            sablist = sab.split(',')
            print sab
            print 'sablist' + sab
            terms = MRCONSO.objects.filter(STR__contains=str).filter(SAB__in=sablist).order_by('CUI')
        else:
            terms = MRCONSO.objects.filter(STR__contains=str).order_by('CUI')

        rterms = []

        for term in terms:
            rterms.append({
                'concept':term.CUI,
                'terms':term.STR,
                'sabs':term.SAB,
            })

        return rterms

    def _get_children(self, cui, sab):
        cursor = connection.cursor()
        if sab:
            cursor.execute("SELECT rel.cui1 as CUI, rel.sab as SAB, conso.str as STR FROM `MRREL` rel, MRCONSO conso WHERE rel.cui2 = conso.cui AND rel.rel = 'CHD' AND rel.rela = 'ISA' AND rel.sab = %s AND rel.cui1 = %s GROUP BY rel.cui1, rel.sab, conso.str", [sab, cui])
        else:
            cursor.execute("SELECT rel.cui1 as CUI, rel.sab as SAB, conso.str as STR FROM `MRREL` rel, MRCONSO conso WHERE rel.cui2 = conso.cui AND rel.rel = 'CHD' AND rel.rela = 'ISA' AND rel.cui1 = %s GROUP BY rel.cui1, rel.sab, conso.str", [cui])
        terms = cursor.fetchall()
        field = cursor.description
        rterms = []

        for row in terms:
            i = 0
            record = {}
            while i < len(field):
                record[field[i][0]] = row[i]
                i = i+1
            rterms.append(record)

        return rterms

    def _get_parent(self, cui, sab):
        cursor = connection.cursor()
        if sab:
            cursor.execute("SELECT rel.cui1 as CUI, rel.sab as SAB, conso.str as STR FROM `MRREL` rel, MRCONSO conso WHERE rel.cui2 = conso.cui AND rel.rel = 'PAR' AND rel.rela = 'inverse_isa' AND rel.sab = %s AND rel.cui1 = %s GROUP BY rel.cui1, rel.sab, conso.str", [sab, cui])
        else:
            cursor.execute("SELECT rel.cui1 as CUI, rel.sab as SAB, conso.str as STR FROM `MRREL` rel, MRCONSO conso WHERE rel.cui2 = conso.cui AND rel.rel = 'PAR' AND rel.rela = 'inverse_isa' AND rel.cui1 = %s GROUP BY rel.cui1, rel.sab, conso.str", [cui])
        terms = cursor.fetchall()
        field = cursor.description
        rterms = []

        for row in terms:
            i = 0
            record = {}
            while i < len(field):
                record[field[i][0]] = row[i]
                i = i+1
            rterms.append(record)

        return rterms

    def _get_synonyms(self, cui, sab):
        print 'syyyyyy'
        print cui
        if sab:
            sablist = sab.split(',')
            print sablist
            terms = MRCONSO.objects.filter(CUI=cui).filter(SAB__in=sablist)
        else:
            terms = MRCONSO.objects.filter(CUI=cui)
        rterms = []
        print 'sssssssss'
        for term in terms:
            rterms.append({
                'terms':term.STR,
            })
        print '11111111'
        return rterms

