# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2022 Michał Góral

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from corgi.org import Organicer
from corgi.functional import unwrap_or_else
from corgi.theme import DEFAULT_THEME as th

from corgi.lick.elements import Section

from corgi.format import style_text, prints

from corgi.node_predicates import *


def scheduled_date(node: Node) -> Optional[Timestamp]:
    if node.children and isinstance(node.children[0].data, Section):
        return node.children[0].data.scheduled


def deadline_date(node: Node) -> Optional[Timestamp]:
    if node.children and isinstance(node.children[0].data, Section):
        return node.children[0].data.deadline


@dataclass
class Task:
    doc: Document
    node: Node
    scheduled: Optional[date] = None
    deadline: Optional[date] = None


def make_tasks(
    tasks: Iterable[Tuple[Document, Node]], split: bool = False
) -> List[Task]:
    """Function which makes "Tasks" from Nodes and Documents. Tasks are wrappers
    which fetch and hold info about task metadata, which typically can be
    accessed by inspecting node's children, in a single, easy to read place.

    Optionally, it can split a single node to 2 tasks if it is both scheduled
    and has a deadline. This simplifies its displaying in a week agenda (Emacs'
    org-mode displays such tasks twice)."""
    ret = []

    for doc, node in tasks:
        sched = scheduled_date(node)
        dead = deadline_date(node)

        if not split or (not sched and not dead):
            ret.append(Task(doc, node, scheduled=sched, deadline=dead))
        else:
            if sched:
                ret.append(Task(doc, node, scheduled=sched))
            if dead:
                ret.append(Task(doc, node, deadline=dead))
    return ret


@dataclass
class OptCmp:
    val: Optional[Any]
    reverse: bool = False

    def __lt__(self, other):
        if self.val and other.val:
            return (self.val < other.val) ^ self.reverse
        # empty optionals are always smaller, no matter the reverse flag
        return not self.val


def cmp_task_importance(task: Task) -> Tuple[...]:
    # reverse explanation:
    # generally sort() uses __lt__ and smaller elements are in the front. We
    # use sort(reverse=True), meaning that higher elements are in the front.
    #
    # - for priority A > B > C, but ASCII-wise comparison yields something
    #   contrary; we want lower ASCII be in front (contrary to global reverse)
    # - for scheduled earlier date means that we missed scheduled time, so it
    #   should be in front, but global reverse makes this order wrong
    # - for deadline same as above
    #
    # So we basically double-reverse everything: globally to indicate that we
    # want to have order items from the most important, and locally, to fix
    # local ordering
    return (
        OptCmp(task.node.data.priority, reverse=True),
        OptCmp(task.scheduled, reverse=True),
        OptCmp(task.deadline, reverse=True),
        task.doc.path,
    )


def cmp_task_priority(task: Task) -> Tuple[...]:
    return (
        OptCmp(task.node.data.priority, reverse=True),
        task.doc.path,
    )


def style_headline(hl: Headline, kw_todo: List[str]) -> str:
    elems = []
    if hl.keyword:
        kw_style = th.todo if hl.keyword in kw_todo else th.done
        elems.append(style_text(hl.keyword, kw_style))
    if hl.priority:
        prio_style_name = f"priority_{hl.priority.upper()}"
        prio_style = getattr(th, prio_style_name, th.normal)
        elems.append(style_text(f"[#{hl.priority}]", prio_style))
    if hl.title:
        elems.append(hl.title)
    if hl.tags:
        elems.append(style_text(f":{':'.join(hl.tags)}:", th.tags))

    return " ".join(elems)


def todo_tasks(org: Organicer, paths: List[str]):
    node_filter = is_visible_task(org.todo_keywords)
    tasks = make_tasks(org.find_nodes(node_filter, paths))
    longest_org_name = min(10, max((len(t.doc.org_name) for t in tasks), default=0))
    tasks.sort(key=cmp_task_priority, reverse=True)

    for task in tasks:
        on = f"{task.doc.org_name[:longest_org_name]}:".ljust(longest_org_name + 4)
        hl = style_headline(task.node.data, org.todo_keywords)
        text = f"  {on} {hl}"
        print(text)


def week_agenda(org: Organicer, paths: List[str]):
    today = date.today()
    task_gather_period = timedelta(days=14)

    # TODO: this probably is too trival and doesn't account strange date
    # exceptions in some timezones, where some king in XV centrury decided that
    # there will be Friday after the next Wednesday.
    monday = today - timedelta(days=today.weekday())
    end = today + task_gather_period

    is_visible = is_visible_task(org.todo_keywords)
    node_filter = planned_between(end=end)

    tasks = make_tasks(org.find_nodes(node_filter, paths), split=True)
    longest_org_name = min(10, max((len(t.doc.org_name) for t in tasks), default=0))

    agenda_length = 7
    days = 0
    day_fmt = "%A %d %B %Y"
    while days < agenda_length:
        day = monday + timedelta(days=days)
        days += 1

        if day == today:
            is_day_task = any_match(
                planned_on(day),
                all_match(
                    is_visible,
                    any_match(deadline_between(end=end), scheduled_between(end=today)),
                ),
            )
            wd_style = th.agenda_today
        else:
            is_day_task = planned_on(day)
            wd_style = th.agenda_day

        # TODO: support for printing hours (time) (mg, 2022-02-23)
        # TODO: highlight weekend (mgoral, 2022-02-23)
        # TODO: highlight overdue tasks (mg, 2022-02-23)
        # TODO: cleanup (mg, 2022-02-23)
        prints(day.strftime(day_fmt), wd_style)

        day_tasks = [t for t in tasks if is_day_task(t.node)]
        day_tasks.sort(key=cmp_task_importance, reverse=True)

        for task in day_tasks:
            # tasks scheduled in the future shouldn't be displayed. They might
            # end up here due to node's deadline and task duplication made by
            # make_tasks()
            if task.scheduled and task.scheduled.date > day:
                continue

            when = ""

            if task.scheduled:
                if task.scheduled.date == day:
                    when = "Scheduled:"
                else:
                    td = abs((day - task.scheduled.date).days)
                    when = f"Sched.{td}x"
            elif task.deadline:
                if task.deadline.date == day:
                    when = "Deadline:"
                else:
                    td = (task.deadline.date - day).days
                    if td < 0:
                        when = f"{abs(td)} d. ago"
                    else:
                        when = f"In {abs(td)} d."

            on = f"{task.doc.org_name[:longest_org_name]}:".ljust(longest_org_name + 2)
            hl = style_headline(task.node.data, org.todo_keywords)
            when = when.ljust(12)

            text = f"  {on} {when} {hl}"
            print(text)


def agenda_view(args, config):
    org = Organicer(config)
    org.load_documents(unwrap_or_else(args.documents, config.org.documents))

    if args.todo:
        return todo_tasks(org, args.filter_paths)
    return week_agenda(org, args.filter_paths)
