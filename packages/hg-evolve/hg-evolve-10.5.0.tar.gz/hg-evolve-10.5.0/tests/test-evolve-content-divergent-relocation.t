======================================================
Tests the resolution of content divergence: relocation
======================================================

This file intend to cover case where changesets need to be moved to different parents

  $ cat >> $HGRCPATH <<EOF
  > [alias]
  > glog = log -GT "{rev}:{node|short} {desc|firstline}\n ({bookmarks}) [{branch}] {phase}"
  > [phases]
  > publish = False
  > [extensions]
  > rebase =
  > EOF
  $ echo "evolve=$(echo $(dirname $TESTDIR))/hgext3rd/evolve/" >> $HGRCPATH


Testing resolution of content-divergent changesets when they are on different
parents and resolution and relocation wont result in conflicts
------------------------------------------------------------------------------

  $ hg init multiparents
  $ cd multiparents
  $ echo ".*\.orig" > .hgignore
  $ hg add .hgignore
  $ hg ci -m "added hgignore"
  $ for ch in a b c d; do echo foo > $ch; hg add $ch; hg ci -qm "added "$ch; done;

  $ hg glog
  @  4:c41c793e0ef1 added d
  |   () [default] draft
  o  3:ca1b80f7960a added c
  |   () [default] draft
  o  2:b1661037fa25 added b
  |   () [default] draft
  o  1:c7586e2a9264 added a
  |   () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg up .^^
  0 files updated, 0 files merged, 2 files removed, 0 files unresolved
  $ echo bar > b
  $ hg amend
  2 new orphan changesets

  $ hg rebase -r b1661037fa25 -d 8fa14d15e168 --hidden --config experimental.evolution.allowdivergence=True
  rebasing 2:b1661037fa25 "added b"
  2 new content-divergent changesets

  $ hg glog
  *  6:da4b96f4a8d6 added b
  |   () [default] draft
  | @  5:7ed0642d644b added b
  | |   () [default] draft
  | | *  4:c41c793e0ef1 added d
  | | |   () [default] draft
  | | *  3:ca1b80f7960a added c
  | | |   () [default] draft
  | | x  2:b1661037fa25 added b
  | |/    () [default] draft
  | o  1:c7586e2a9264 added a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

In this case, we have two divergent changeset:
- one did not changed parent
- the other did changed parent

So we can do a 3 way merges merges. on one side we have changes (the parent
change) and on the other one we don't, we should apply the change.

  $ hg evolve --list --rev 'contentdivergent()'
  7ed0642d644b: added b
    content-divergent: da4b96f4a8d6 (draft) (precursor b1661037fa25)
  
  da4b96f4a8d6: added b
    content-divergent: 7ed0642d644b (draft) (precursor b1661037fa25)
  

  $ hg glog --hidden --rev '::(7ed0642d644b+da4b96f4a8d6+b1661037fa25)'
  *  6:da4b96f4a8d6 added b
  |   () [default] draft
  | @  5:7ed0642d644b added b
  | |   () [default] draft
  | | x  2:b1661037fa25 added b
  | |/    () [default] draft
  | o  1:c7586e2a9264 added a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg evolve --content-divergent
  merge:[5] added b
  with: [6] added b
  base: [2] added b
  rebasing "divergent" content-divergent changeset 7ed0642d644b on 8fa14d15e168
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  working directory is now at c5862ade0278

  $ hg glog
  @  8:c5862ade0278 added b
  |   () [default] draft
  | *  4:c41c793e0ef1 added d
  | |   () [default] draft
  | *  3:ca1b80f7960a added c
  | |   () [default] draft
  | x  2:b1661037fa25 added b
  | |   () [default] draft
  | o  1:c7586e2a9264 added a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg exp
  # HG changeset patch
  # User test
  # Date 0 0
  #      Thu Jan 01 00:00:00 1970 +0000
  # Node ID c5862ade02783a99f46082f4f0483c449fc4c3f2
  # Parent  8fa14d15e1684a9720b1b065aba9d5ea51024cb2
  added b
  
  diff -r 8fa14d15e168 -r c5862ade0278 b
  --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  +++ b/b	Thu Jan 01 00:00:00 1970 +0000
  @@ -0,0 +1,1 @@
  +bar

  $ hg debugobsolete
  b1661037fa25511d0b7ccddf405e336f9d7d3424 7ed0642d644bb9ad93d252dd9ffe7b4729febe48 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'amend', 'user': 'test'}
  b1661037fa25511d0b7ccddf405e336f9d7d3424 da4b96f4a8d610a85b225583138f681d67e275dd 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'rebase', 'user': 'test'}
  7ed0642d644bb9ad93d252dd9ffe7b4729febe48 2ec52f302b0f0ef30979124e92f1d9f2a26cedf8 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  2ec52f302b0f0ef30979124e92f1d9f2a26cedf8 c5862ade02783a99f46082f4f0483c449fc4c3f2 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '0', 'operation': 'evolve', 'user': 'test'}
  da4b96f4a8d610a85b225583138f681d67e275dd c5862ade02783a99f46082f4f0483c449fc4c3f2 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'evolve', 'user': 'test'}
  $ hg obslog --all
  @    c5862ade0278 (8) added b
  |\     rewritten from 2ec52f302b0f using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |    amended(content) from da4b96f4a8d6 using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  x |  2ec52f302b0f (7) added b
  | |    rebased(parent) from 7ed0642d644b using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  | x  da4b96f4a8d6 (6) added b
  | |    rebased(parent) from b1661037fa25 using rebase by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  x |  7ed0642d644b (5) added b
  |/     amended(content) from b1661037fa25 using amend by test (Thu Jan 01 00:00:00 1970 +0000)
  |
  x  b1661037fa25 (2) added b
  

Resolving orphans to get back to a normal graph

  $ hg evolve --all
  move:[3] added c
  atop:[8] added b
  move:[4] added d
  $ hg glog
  o  10:25cb1649b463 added d
  |   () [default] draft
  o  9:81ead2f9fc61 added c
  |   () [default] draft
  @  8:c5862ade0278 added b
  |   () [default] draft
  | o  1:c7586e2a9264 added a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

More testing!

  $ echo x > x
  $ hg ci -Aqm "added x"
  $ hg glog -r .
  @  11:f220d694b3a6 added x
  |   () [default] draft
  ~

  $ echo foo > x
  $ hg branch bar
  marked working directory as branch bar
  (branches are permanent and global, did you want a bookmark?)
  $ hg amend -m "added foo to x"

  $ hg up 'predecessors(.)' --hidden
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  updated to hidden changeset f220d694b3a6
  (hidden revision 'f220d694b3a6' was rewritten as: 91939f44a1fe)
  working directory parent is obsolete! (f220d694b3a6)
  (use 'hg evolve' to update to its successor: 91939f44a1fe)
  $ hg rebase -r . -d 'desc("added d")' --config experimental.evolution.allowdivergence=True
  rebasing 11:f220d694b3a6 "added x"
  2 new content-divergent changesets

  $ hg glog
  @  13:7af6be6736c0 added x
  |   () [default] draft
  | *  12:91939f44a1fe added foo to x
  | |   () [bar] draft
  o |  10:25cb1649b463 added d
  | |   () [default] draft
  o |  9:81ead2f9fc61 added c
  |/    () [default] draft
  o  8:c5862ade0278 added b
  |   () [default] draft
  | o  1:c7586e2a9264 added a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg evolve --content-divergent
  merge:[12] added foo to x
  with: [13] added x
  base: [11] added x
  rebasing "divergent" content-divergent changeset 91939f44a1fe on 25cb1649b463
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  working directory is now at 3c4c7420a968

  $ hg exp
  # HG changeset patch
  # User test
  # Date 0 0
  #      Thu Jan 01 00:00:00 1970 +0000
  # Branch bar
  # Node ID 3c4c7420a968a3f76d61fa16c3af9abe115f07b6
  # Parent  25cb1649b46389f8e6e77c3796f01b37996b8fcd
  added foo to x
  
  diff -r 25cb1649b463 -r 3c4c7420a968 x
  --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  +++ b/x	Thu Jan 01 00:00:00 1970 +0000
  @@ -0,0 +1,1 @@
  +foo

The above `hg exp` and the following log call demonstrates that message, content
and branch change is preserved in case of relocation
  $ hg glog
  @  15:3c4c7420a968 added foo to x
  |   () [bar] draft
  o  10:25cb1649b463 added d
  |   () [default] draft
  o  9:81ead2f9fc61 added c
  |   () [default] draft
  o  8:c5862ade0278 added b
  |   () [default] draft
  | o  1:c7586e2a9264 added a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg debugobsolete
  b1661037fa25511d0b7ccddf405e336f9d7d3424 7ed0642d644bb9ad93d252dd9ffe7b4729febe48 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'amend', 'user': 'test'}
  b1661037fa25511d0b7ccddf405e336f9d7d3424 da4b96f4a8d610a85b225583138f681d67e275dd 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'rebase', 'user': 'test'}
  7ed0642d644bb9ad93d252dd9ffe7b4729febe48 2ec52f302b0f0ef30979124e92f1d9f2a26cedf8 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  2ec52f302b0f0ef30979124e92f1d9f2a26cedf8 c5862ade02783a99f46082f4f0483c449fc4c3f2 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '0', 'operation': 'evolve', 'user': 'test'}
  da4b96f4a8d610a85b225583138f681d67e275dd c5862ade02783a99f46082f4f0483c449fc4c3f2 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'evolve', 'user': 'test'}
  ca1b80f7960aae2306287bab52b4090c59af8c29 81ead2f9fc6156de69d12b7b5df71c34ab8b9c10 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  c41c793e0ef1ddb463e85ea9491e377d01127ba2 25cb1649b46389f8e6e77c3796f01b37996b8fcd 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  f220d694b3a605e236b4b34ef97d3cc6959efb89 91939f44a1fe6d865ec791122014971dfff75129 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '73', 'operation': 'amend', 'user': 'test'}
  f220d694b3a605e236b4b34ef97d3cc6959efb89 7af6be6736c0aebd226820373190e636fe9f16e9 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'rebase', 'user': 'test'}
  91939f44a1fe6d865ec791122014971dfff75129 c38f731f5ae01e417ceeea09f046febf4536d356 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  c38f731f5ae01e417ceeea09f046febf4536d356 3c4c7420a968a3f76d61fa16c3af9abe115f07b6 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '0', 'operation': 'evolve', 'user': 'test'}
  7af6be6736c0aebd226820373190e636fe9f16e9 3c4c7420a968a3f76d61fa16c3af9abe115f07b6 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '73', 'operation': 'evolve', 'user': 'test'}
  $ hg obslog --all
  @    3c4c7420a968 (15) added foo to x
  |\     rewritten(description, branch, content) from 7af6be6736c0 using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |    rewritten from c38f731f5ae0 using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  x |  7af6be6736c0 (13) added x
  | |    rebased(parent) from f220d694b3a6 using rebase by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  | x  c38f731f5ae0 (14) added foo to x
  | |    rebased(parent) from 91939f44a1fe using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  | x  91939f44a1fe (12) added foo to x
  |/     rewritten(description, branch, content) from f220d694b3a6 using amend by test (Thu Jan 01 00:00:00 1970 +0000)
  |
  x  f220d694b3a6 (11) added x
  

Testing when both the content-divergence are on different parents and resolution
will lead to conflicts
---------------------------------------------------------------------------------

  $ hg up .^^^
  0 files updated, 0 files merged, 3 files removed, 0 files unresolved

  $ echo y > y
  $ hg ci -Aqm "added y"
  $ hg glog -r .
  @  16:d84c9e99d55b added y
  |   () [default] draft
  ~

  $ echo bar > y
  $ hg amend

  $ hg up 'predecessors(.)' --hidden
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  updated to hidden changeset d84c9e99d55b
  (hidden revision 'd84c9e99d55b' was rewritten as: 98cd38d20303)
  working directory parent is obsolete! (d84c9e99d55b)
  (use 'hg evolve' to update to its successor: 98cd38d20303)
  $ hg rebase -r . -d 'desc("added foo to x")' --config experimental.evolution.allowdivergence=True
  rebasing 16:d84c9e99d55b "added y"
  2 new content-divergent changesets
  $ echo wat > y
  $ hg amend

  $ hg glog
  @  19:ec9ec45c397e added y
  |   () [bar] draft
  | *  17:98cd38d20303 added y
  | |   () [default] draft
  o |  15:3c4c7420a968 added foo to x
  | |   () [bar] draft
  o |  10:25cb1649b463 added d
  | |   () [default] draft
  o |  9:81ead2f9fc61 added c
  |/    () [default] draft
  o  8:c5862ade0278 added b
  |   () [default] draft
  | o  1:c7586e2a9264 added a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg evolve --content-divergent
  merge:[17] added y
  with: [19] added y
  base: [16] added y
  rebasing "divergent" content-divergent changeset 98cd38d20303 on 3c4c7420a968
  merging y
  warning: conflicts while merging y! (edit, then use 'hg resolve --mark')
  0 files updated, 0 files merged, 0 files removed, 1 files unresolved
  unresolved merge conflicts
  (see 'hg help evolve.interrupted')
  [240]

  $ echo watbar > y
  $ hg resolve -m
  (no more unresolved files)
  continue: hg evolve --continue
  $ hg evolve --continue
  working directory is now at 26dd4974d99f

  $ hg glog
  @  21:26dd4974d99f added y
  |   () [bar] draft
  o  15:3c4c7420a968 added foo to x
  |   () [bar] draft
  o  10:25cb1649b463 added d
  |   () [default] draft
  o  9:81ead2f9fc61 added c
  |   () [default] draft
  o  8:c5862ade0278 added b
  |   () [default] draft
  | o  1:c7586e2a9264 added a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg debugobsolete
  b1661037fa25511d0b7ccddf405e336f9d7d3424 7ed0642d644bb9ad93d252dd9ffe7b4729febe48 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'amend', 'user': 'test'}
  b1661037fa25511d0b7ccddf405e336f9d7d3424 da4b96f4a8d610a85b225583138f681d67e275dd 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'rebase', 'user': 'test'}
  7ed0642d644bb9ad93d252dd9ffe7b4729febe48 2ec52f302b0f0ef30979124e92f1d9f2a26cedf8 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  2ec52f302b0f0ef30979124e92f1d9f2a26cedf8 c5862ade02783a99f46082f4f0483c449fc4c3f2 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '0', 'operation': 'evolve', 'user': 'test'}
  da4b96f4a8d610a85b225583138f681d67e275dd c5862ade02783a99f46082f4f0483c449fc4c3f2 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'evolve', 'user': 'test'}
  ca1b80f7960aae2306287bab52b4090c59af8c29 81ead2f9fc6156de69d12b7b5df71c34ab8b9c10 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  c41c793e0ef1ddb463e85ea9491e377d01127ba2 25cb1649b46389f8e6e77c3796f01b37996b8fcd 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  f220d694b3a605e236b4b34ef97d3cc6959efb89 91939f44a1fe6d865ec791122014971dfff75129 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '73', 'operation': 'amend', 'user': 'test'}
  f220d694b3a605e236b4b34ef97d3cc6959efb89 7af6be6736c0aebd226820373190e636fe9f16e9 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'rebase', 'user': 'test'}
  91939f44a1fe6d865ec791122014971dfff75129 c38f731f5ae01e417ceeea09f046febf4536d356 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  c38f731f5ae01e417ceeea09f046febf4536d356 3c4c7420a968a3f76d61fa16c3af9abe115f07b6 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '0', 'operation': 'evolve', 'user': 'test'}
  7af6be6736c0aebd226820373190e636fe9f16e9 3c4c7420a968a3f76d61fa16c3af9abe115f07b6 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '73', 'operation': 'evolve', 'user': 'test'}
  d84c9e99d55bfa499ab77dabd1fb3035e8f14ba9 98cd38d203030c04c89650c7280a6a71ae2f748c 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'amend', 'user': 'test'}
  d84c9e99d55bfa499ab77dabd1fb3035e8f14ba9 6c3124aac43f4c0e64155b93ea60e0e10abd6ba1 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '68', 'operation': 'rebase', 'user': 'test'}
  6c3124aac43f4c0e64155b93ea60e0e10abd6ba1 ec9ec45c397e15dfd9f25a91b6ffa1e17f9b9471 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'amend', 'user': 'test'}
  98cd38d203030c04c89650c7280a6a71ae2f748c 5ddc0bec0e2650fb56e3b5d24f7c7c3a61401fbe 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  5ddc0bec0e2650fb56e3b5d24f7c7c3a61401fbe 26dd4974d99f30b9c9b259e22254b29474155d45 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '72', 'operation': 'evolve', 'user': 'test'}
  ec9ec45c397e15dfd9f25a91b6ffa1e17f9b9471 26dd4974d99f30b9c9b259e22254b29474155d45 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'evolve', 'user': 'test'}
  $ hg obslog -r . --all
  @    26dd4974d99f (21) added y
  |\     rewritten(branch, content) from 5ddc0bec0e26 using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |    amended(content) from ec9ec45c397e using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  x |  5ddc0bec0e26 (20) added y
  | |    rebased(parent) from 98cd38d20303 using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  | x  ec9ec45c397e (19) added y
  | |    amended(content) from 6c3124aac43f using amend by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  | x  6c3124aac43f (18) added y
  | |    rewritten(branch, parent) from d84c9e99d55b using rebase by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  x |  98cd38d20303 (17) added y
  |/     amended(content) from d84c9e99d55b using amend by test (Thu Jan 01 00:00:00 1970 +0000)
  |
  x  d84c9e99d55b (16) added y
  

checking that relocated commit is there
  $ hg exp 20 --hidden
  # HG changeset patch
  # User test
  # Date 0 0
  #      Thu Jan 01 00:00:00 1970 +0000
  # Node ID 5ddc0bec0e2650fb56e3b5d24f7c7c3a61401fbe
  # Parent  3c4c7420a968a3f76d61fa16c3af9abe115f07b6
  added y
  
  diff -r 3c4c7420a968 -r 5ddc0bec0e26 y
  --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  +++ b/y	Thu Jan 01 00:00:00 1970 +0000
  @@ -0,0 +1,1 @@
  +bar

Testing when the relocation will result in conflicts and merging also:
----------------------------------------------------------------------

  $ hg glog
  @  21:26dd4974d99f added y
  |   () [bar] draft
  o  15:3c4c7420a968 added foo to x
  |   () [bar] draft
  o  10:25cb1649b463 added d
  |   () [default] draft
  o  9:81ead2f9fc61 added c
  |   () [default] draft
  o  8:c5862ade0278 added b
  |   () [default] draft
  | o  1:c7586e2a9264 added a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg up .^^^^
  0 files updated, 0 files merged, 4 files removed, 0 files unresolved

  $ echo z > z
  $ hg ci -Aqm "added z"
  $ hg glog -r .
  @  22:136e58088ce2 added z
  |   () [default] draft
  ~

  $ echo foo > y
  $ hg add y
  $ hg amend

  $ hg up 'predecessors(.)' --hidden
  0 files updated, 0 files merged, 1 files removed, 0 files unresolved
  updated to hidden changeset 136e58088ce2
  (hidden revision '136e58088ce2' was rewritten as: f4c3594c72e7)
  working directory parent is obsolete! (136e58088ce2)
  (use 'hg evolve' to update to its successor: f4c3594c72e7)
  $ hg rebase -r . -d 'desc("added y")' --config experimental.evolution.allowdivergence=True
  rebasing 22:136e58088ce2 "added z"
  2 new content-divergent changesets
  $ echo bar > z
  $ hg amend

  $ hg glog
  @  25:7e87b40e3aa8 added z
  |   () [bar] draft
  | *  23:f4c3594c72e7 added z
  | |   () [default] draft
  o |  21:26dd4974d99f added y
  | |   () [bar] draft
  o |  15:3c4c7420a968 added foo to x
  | |   () [bar] draft
  o |  10:25cb1649b463 added d
  | |   () [default] draft
  o |  9:81ead2f9fc61 added c
  |/    () [default] draft
  o  8:c5862ade0278 added b
  |   () [default] draft
  | o  1:c7586e2a9264 added a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg evolve --content-divergent --any
  merge:[23] added z
  with: [25] added z
  base: [22] added z
  rebasing "divergent" content-divergent changeset f4c3594c72e7 on 26dd4974d99f
  merging y
  warning: conflicts while merging y! (edit, then use 'hg resolve --mark')
  unresolved merge conflicts
  (see 'hg help evolve.interrupted')
  [240]

  $ hg diff
  diff -r 26dd4974d99f y
  --- a/y	Thu Jan 01 00:00:00 1970 +0000
  +++ b/y	Thu Jan 01 00:00:00 1970 +0000
  @@ -1,1 +1,5 @@
  +<<<<<<< destination: 26dd4974d99f bar - test: added y
   watbar
  +=======
  +foo
  +>>>>>>> evolving:    f4c3594c72e7 - test: added z
  diff -r 26dd4974d99f z
  --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  +++ b/z	Thu Jan 01 00:00:00 1970 +0000
  @@ -0,0 +1,1 @@
  +z

  $ echo foo > y
  $ hg resolve -m
  (no more unresolved files)
  continue: hg evolve --continue

  $ hg evolve --continue
  evolving 23:f4c3594c72e7 "added z"
  merging y
  warning: conflicts while merging y! (edit, then use 'hg resolve --mark')
  1 files updated, 0 files merged, 0 files removed, 1 files unresolved
  unresolved merge conflicts
  (see 'hg help evolve.interrupted')
  [240]

  $ hg diff
  diff -r 5049972c0e21 y
  --- a/y	Thu Jan 01 00:00:00 1970 +0000
  +++ b/y	Thu Jan 01 00:00:00 1970 +0000
  @@ -1,1 +1,5 @@
  +<<<<<<< local: 5049972c0e21 - test: added z
   foo
  +=======
  +watbar
  +>>>>>>> other: 7e87b40e3aa8 bar - test: added z
  diff -r 5049972c0e21 z
  --- a/z	Thu Jan 01 00:00:00 1970 +0000
  +++ b/z	Thu Jan 01 00:00:00 1970 +0000
  @@ -1,1 +1,1 @@
  -z
  +bar

  $ echo foo > y
  $ hg resolve -m
  (no more unresolved files)
  continue: hg evolve --continue
  $ hg evolve --continue
  working directory is now at 04eb6e8d253d

  $ hg glog
  @  27:04eb6e8d253d added z
  |   () [bar] draft
  o  21:26dd4974d99f added y
  |   () [bar] draft
  o  15:3c4c7420a968 added foo to x
  |   () [bar] draft
  o  10:25cb1649b463 added d
  |   () [default] draft
  o  9:81ead2f9fc61 added c
  |   () [default] draft
  o  8:c5862ade0278 added b
  |   () [default] draft
  | o  1:c7586e2a9264 added a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg exp
  # HG changeset patch
  # User test
  # Date 0 0
  #      Thu Jan 01 00:00:00 1970 +0000
  # Branch bar
  # Node ID 04eb6e8d253d5f17e0d9b1518678e015c272704e
  # Parent  26dd4974d99f30b9c9b259e22254b29474155d45
  added z
  
  diff -r 26dd4974d99f -r 04eb6e8d253d y
  --- a/y	Thu Jan 01 00:00:00 1970 +0000
  +++ b/y	Thu Jan 01 00:00:00 1970 +0000
  @@ -1,1 +1,1 @@
  -watbar
  +foo
  diff -r 26dd4974d99f -r 04eb6e8d253d z
  --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  +++ b/z	Thu Jan 01 00:00:00 1970 +0000
  @@ -0,0 +1,1 @@
  +bar

  $ hg debugobsolete
  b1661037fa25511d0b7ccddf405e336f9d7d3424 7ed0642d644bb9ad93d252dd9ffe7b4729febe48 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'amend', 'user': 'test'}
  b1661037fa25511d0b7ccddf405e336f9d7d3424 da4b96f4a8d610a85b225583138f681d67e275dd 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'rebase', 'user': 'test'}
  7ed0642d644bb9ad93d252dd9ffe7b4729febe48 2ec52f302b0f0ef30979124e92f1d9f2a26cedf8 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  2ec52f302b0f0ef30979124e92f1d9f2a26cedf8 c5862ade02783a99f46082f4f0483c449fc4c3f2 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '0', 'operation': 'evolve', 'user': 'test'}
  da4b96f4a8d610a85b225583138f681d67e275dd c5862ade02783a99f46082f4f0483c449fc4c3f2 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'evolve', 'user': 'test'}
  ca1b80f7960aae2306287bab52b4090c59af8c29 81ead2f9fc6156de69d12b7b5df71c34ab8b9c10 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  c41c793e0ef1ddb463e85ea9491e377d01127ba2 25cb1649b46389f8e6e77c3796f01b37996b8fcd 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  f220d694b3a605e236b4b34ef97d3cc6959efb89 91939f44a1fe6d865ec791122014971dfff75129 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '73', 'operation': 'amend', 'user': 'test'}
  f220d694b3a605e236b4b34ef97d3cc6959efb89 7af6be6736c0aebd226820373190e636fe9f16e9 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'rebase', 'user': 'test'}
  91939f44a1fe6d865ec791122014971dfff75129 c38f731f5ae01e417ceeea09f046febf4536d356 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  c38f731f5ae01e417ceeea09f046febf4536d356 3c4c7420a968a3f76d61fa16c3af9abe115f07b6 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '0', 'operation': 'evolve', 'user': 'test'}
  7af6be6736c0aebd226820373190e636fe9f16e9 3c4c7420a968a3f76d61fa16c3af9abe115f07b6 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '73', 'operation': 'evolve', 'user': 'test'}
  d84c9e99d55bfa499ab77dabd1fb3035e8f14ba9 98cd38d203030c04c89650c7280a6a71ae2f748c 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'amend', 'user': 'test'}
  d84c9e99d55bfa499ab77dabd1fb3035e8f14ba9 6c3124aac43f4c0e64155b93ea60e0e10abd6ba1 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '68', 'operation': 'rebase', 'user': 'test'}
  6c3124aac43f4c0e64155b93ea60e0e10abd6ba1 ec9ec45c397e15dfd9f25a91b6ffa1e17f9b9471 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'amend', 'user': 'test'}
  98cd38d203030c04c89650c7280a6a71ae2f748c 5ddc0bec0e2650fb56e3b5d24f7c7c3a61401fbe 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  5ddc0bec0e2650fb56e3b5d24f7c7c3a61401fbe 26dd4974d99f30b9c9b259e22254b29474155d45 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '72', 'operation': 'evolve', 'user': 'test'}
  ec9ec45c397e15dfd9f25a91b6ffa1e17f9b9471 26dd4974d99f30b9c9b259e22254b29474155d45 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'evolve', 'user': 'test'}
  136e58088ce2a46749c73256b02608ca9be0fe09 f4c3594c72e7140404222d25e8827292e5d1a728 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'amend', 'user': 'test'}
  136e58088ce2a46749c73256b02608ca9be0fe09 da49edc1732932755e2c42d91b6883e6616ff40b 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '68', 'operation': 'rebase', 'user': 'test'}
  da49edc1732932755e2c42d91b6883e6616ff40b 7e87b40e3aa8d28f0ba07c1cec4f562e57ba7c12 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'amend', 'user': 'test'}
  f4c3594c72e7140404222d25e8827292e5d1a728 5049972c0e212e0ad051e628b37d162097944b5f 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '12', 'operation': 'evolve', 'user': 'test'}
  5049972c0e212e0ad051e628b37d162097944b5f 04eb6e8d253d5f17e0d9b1518678e015c272704e 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '72', 'operation': 'evolve', 'user': 'test'}
  7e87b40e3aa8d28f0ba07c1cec4f562e57ba7c12 04eb6e8d253d5f17e0d9b1518678e015c272704e 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'evolve', 'user': 'test'}
  $ hg obslog --all
  @    04eb6e8d253d (27) added z
  |\     rewritten(branch, content) from 5049972c0e21 using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |    amended(content) from 7e87b40e3aa8 using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  x |  5049972c0e21 (26) added z
  | |    rewritten(parent, content) from f4c3594c72e7 using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  | x  7e87b40e3aa8 (25) added z
  | |    amended(content) from da49edc17329 using amend by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  | x  da49edc17329 (24) added z
  | |    rewritten(branch, parent) from 136e58088ce2 using rebase by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  x |  f4c3594c72e7 (23) added z
  |/     amended(content) from 136e58088ce2 using amend by test (Thu Jan 01 00:00:00 1970 +0000)
  |
  x  136e58088ce2 (22) added z
  

  $ cd ..

Testing when relocation results in nothing to commit
----------------------------------------------------

Set up a repo where relocation results in no changes to commit because the
changes from the relocated node are already in the destination.

  $ hg init nothing-to-commit
  $ cd nothing-to-commit
  $ echo 0 > a
  $ hg ci -Aqm initial
  $ echo 1 > a
  $ hg ci -Aqm upstream
  $ hg prev -q

Create the source of divergence.
  $ echo 0 > b
  $ hg ci -Aqm divergent

The first side of the divergence get rebased on top of upstream.
  $ hg rebase -r . -d 'desc("upstream")'
  rebasing 2:898ddd4443b3 tip "divergent"
  $ hg --hidden co 2 -q
  updated to hidden changeset 898ddd4443b3
  (hidden revision '898ddd4443b3' was rewritten as: befae6138569)
  working directory parent is obsolete! (898ddd4443b3)

The other side of the divergence gets amended so it matches upstream.
Relocation (onto upstream) will therefore result in no changes to commit.
  $ hg revert -r 'desc("upstream")' --all
  removing b
  reverting a
  $ hg amend --config experimental.evolution.allowdivergence=True
  2 new content-divergent changesets

Add a commit on top. This one should become an orphan. Evolving it later
should put it on top of the other divergent side (the one that's on top of
upstream)
  $ echo 0 > c
  $ hg ci -Aqm child
  $ hg co -q null
  $ hg glog
  o  5:88473f9137d1 child
  |   () [default] draft
  *  4:4cc21313ecee divergent
  |   () [default] draft
  | *  3:befae6138569 divergent
  | |   () [default] draft
  | o  1:33c576d20069 upstream
  |/    () [default] draft
  o  0:98a3f8f02ba7 initial
      () [default] draft
  $ hg evolve --content-divergent
  merge:[3] divergent
  with: [4] divergent
  base: [2] divergent
  rebasing "other" content-divergent changeset 4cc21313ecee on 33c576d20069
  0 files updated, 0 files merged, 1 files removed, 0 files unresolved
  1 new orphan changesets
  $ hg glog
  o  7:cc3d0c6117c7 divergent
  |   () [default] draft
  | *  5:88473f9137d1 child
  | |   () [default] draft
  | x  4:4cc21313ecee divergent
  | |   () [default] draft
  o |  1:33c576d20069 upstream
  |/    () [default] draft
  o  0:98a3f8f02ba7 initial
      () [default] draft

  $ hg evolve --any
  move:[5] child
  atop:[7] divergent
  $ hg glog
  o  8:916b4ec3b91f child
  |   () [default] draft
  o  7:cc3d0c6117c7 divergent
  |   () [default] draft
  o  1:33c576d20069 upstream
  |   () [default] draft
  o  0:98a3f8f02ba7 initial
      () [default] draft
  $ hg debugobsolete
  898ddd4443b3d5520bf48f22f9411d5a0751cf2e befae61385695f1ae4b78b030ad91075b2b523ef 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'rebase', 'user': 'test'}
  898ddd4443b3d5520bf48f22f9411d5a0751cf2e 4cc21313ecee97ce33265514a0596a192bfa6b3f 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'amend', 'user': 'test'}
  4cc21313ecee97ce33265514a0596a192bfa6b3f bf4fe3a3afeb14c338094f41a35863921856592f 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '12', 'operation': 'evolve', 'user': 'test'}
  befae61385695f1ae4b78b030ad91075b2b523ef cc3d0c6117c7400995107497370fa4c2138399cd 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '8', 'operation': 'evolve', 'user': 'test'}
  bf4fe3a3afeb14c338094f41a35863921856592f cc3d0c6117c7400995107497370fa4c2138399cd 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '0', 'operation': 'evolve', 'user': 'test'}
  88473f9137d12e90055d30bbb9b78dd786520870 916b4ec3b91fd03826bd4b179051ae3cee633b56 0 (Thu Jan 01 00:00:00 1970 +0000) {'ef1': '4', 'operation': 'evolve', 'user': 'test'}
  $ hg obslog -r 'desc("divergent")' --all
  o    cc3d0c6117c7 (7) divergent
  |\     amended(content) from befae6138569 using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |    rewritten from bf4fe3a3afeb using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  x |  befae6138569 (3) divergent
  | |    rebased(parent) from 898ddd4443b3 using rebase by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  | x  bf4fe3a3afeb (6) divergent
  | |    rewritten(parent, content) from 4cc21313ecee using evolve by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  | x  4cc21313ecee (4) divergent
  |/     amended(content) from 898ddd4443b3 using amend by test (Thu Jan 01 00:00:00 1970 +0000)
  |
  x  898ddd4443b3 (2) divergent
  
  $ cd ..
