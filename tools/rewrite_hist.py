import glob
import os
import logging
import copy
import datetime

import biothings
import config
biothings.config_for_app(config)
import pymongo
import biothings.utils.common
import biothings.dataload.storage as storage
import biothings.utils.jsondiff

db = pymongo.MongoClient("mongodb://xxxx:xxxxx")["dev_bioreel"]
diffs_col = db["diffs"]
diffs_store = storage.BasicStorage(db,"diffs",logging)  
patches_store = storage.IgnoreDuplicatedStorage(db,"diffs_jsonpatch",logging)  
diffsjson_col = db["diffs_jsonpatch"]

# will start from there, the v2
v2 = pymongo.MongoClient("mongodb://xxxxx:yyyyyyyyyyyy@zzzz")["genedoc"]
genedoc = v2["genedoc_mygene_allspecies_20160626_ccl30eni"]

def process_add(adds,ts):
    for id in adds:
        yield {"bid":id,'diff': {'op': 'add'},"timestamp":ts,"type":"gene"}

def process_delete(dels,ts):
    for id in dels:
        yield {"bid":id,'diff': {'op': 'delete'},"timestamp":ts,"type":"gene"}

def process_update(ups,ts):
    for up in ups:
        id = up.pop("_id")
        yield {
            "bid":id,
            'diff': {'op': 'update', 'changes': up},
            "timestamp":ts,
            "type":"gene"}

def process(filename):
    logging.info("Processing %s" % filename)
    d = biothings.utils.common.loadobj(filename)
    diffs_store.process(process_add(d["add"],d["timestamp"]),100000)
    diffs_store.process(process_delete(d["delete"],d["timestamp"]),100000)
    diffs_store.process(process_update(d["update"],d["timestamp"]),100000)
    d = None


def process_all(folder):
    for fn in sorted(glob.glob(os.path.join(folder,"*allspecies.pyobj"))):
        process(fn)


def apply(doc,diff):
    for delete in diff["delete"]:
        try:
            doc.pop(delete)
        except KeyError:
            #print("Tried to delete key '%s' but no in doc, ignoring" % delete)
            pass
    for add in diff["add"]:
        doc[add] = diff["add"][add]
    for update in diff["update"]:
        doc[update] = diff["update"][update]

    return doc


def rewrite_history(bid,fromdt=datetime.datetime(2016,7,5,0,0)):
    # fromdt is the next date from which we have diffs computed against root doc from v2
    # starting from v2:
    #print("bid: %s" % bid)
    root = genedoc.find_one({"_id":bid})
    if not root:
        raise ValueError("Can't find root document %s" % repr(bid))
    diffs = diffs_col.find({"bid":bid, "timestamp":{"$gte":fromdt}},no_cursor_timeout=True).sort([("timestamp",1)])
    for diff in diffs:
        try:
            if "changes" in diff["diff"]:
                # rebuild doc with the patch...
                doc = copy.deepcopy(root)
                doc = apply(doc,diff["diff"]["changes"])
                # ... and recompute diffs using jsondiff
                # use_list_ops=True will give max details
                newdiff = biothings.utils.jsondiff.make(root,doc,use_list_ops=True)
                if not newdiff:
                    continue
                    # this can happen when the patch contains key not in the root doc
                    # so diffs between root and new doc are the same (no diff)
                patch = {"bid" : bid,
                         "timestamp" : diff["timestamp"],
                         "type" : "gene",
                         "diff" : newdiff}
                root = doc
            else:
                # not a "change", could be a document being deleted for instance
                patch = {"bid" : bid,
                         "timestamp" : diff["timestamp"],
                         "type" : "gene",
                         "diff" : diff["diff"]}
            yield patch
            # move forward
        except KeyError as e:
            print("err %s, %s" % (e,diff))
            raise


def rewrite_all_history(fromdt=datetime.datetime(2016,7,5,0,0)):
    def iter():
        for dbid in diffs_col.find({},{"bid":1},no_cursor_timeout=True):
            bid = dbid["bid"]
            done = diffsjson_col.find_one({"bid":bid})
            if done:
                print("%s done, skip" % bid)
                continue
            try:
                for doc in rewrite_history(bid,fromdt):
                    yield doc
            except ValueError as e:
                print("no such doc ? %s" % e)

    patches_store.process(iter(),10000)


