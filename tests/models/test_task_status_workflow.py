# -*- coding: utf-8 -*-
# stalker
# Copyright (C) 2013 Erkan Ozgur Yilmaz
#
# This file is part of stalker.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import datetime
import tempfile
import unittest2
from stalker.db import DBSession
from stalker import (db, User, Status, StatusList, Repository, Project, Task,
                     Type, TimeLog)
from stalker.exceptions import StatusError


class TaskStatusWorkflowTestCase(unittest2.TestCase):
    """tests the Task Status Workflow
    """

    def setUp(self):
        """setup the test
        """
        db.setup({'sqlalchemy.url': 'sqlite:///:memory:'})
        db.init()

        # test users
        self.test_user1 = User(
            name='Test User 1',
            login='tuser1',
            email='tuser1@test.com',
            password='secret'
        )
        DBSession.add(self.test_user1)

        self.test_user2 = User(
            name='Test User 2',
            login='tuser2',
            email='tuser2@test.com',
            password='secret'
        )
        DBSession.add(self.test_user2)

        # create a couple of tasks
        self.status_wfd = Status.query.filter_by(code='WFD').first()
        self.status_rts = Status.query.filter_by(code='RTS').first()
        self.status_wip = Status.query.filter_by(code='WIP').first()
        self.status_prev = Status.query.filter_by(code='PREV').first()
        self.status_hrev = Status.query.filter_by(code='HREV').first()
        self.status_drev = Status.query.filter_by(code='DREV').first()
        self.status_oh = Status.query.filter_by(code='OH').first()
        self.status_stop = Status.query.filter_by(code='STOP').first()
        self.status_cmpl = Status.query.filter_by(code='CMPL').first()

        self.test_project_status_list = StatusList(
            name='Project Statuses',
            target_entity_type='Project',
            statuses=[self.status_wfd, self.status_wip,
                      self.status_cmpl]
        )
        DBSession.add(self.test_project_status_list)

        self.test_task_statuses = StatusList.query\
            .filter_by(target_entity_type='Task').first()
        DBSession.add(self.test_task_statuses)

        # repository
        tempdir = tempfile.gettempdir()
        self.test_repo = Repository(
            name='Test Repository',
            linux_path=tempdir,
            windows_path=tempdir,
            osx_path=tempdir
        )
        DBSession.add(self.test_repo)

        # proj1
        self.test_project1 = Project(
            name='Test Project 1',
            code='TProj1',
            status_list=self.test_project_status_list,
            repository=self.test_repo,
            start=datetime.datetime(2013, 6, 20, 0, 0, 0),
            end=datetime.datetime(2013, 6, 30, 0, 0, 0),
            lead=self.test_user1
        )
        DBSession.add(self.test_project1)

        # root tasks
        self.test_task1 = Task(
            name='Test Task 1',
            project=self.test_project1,
            status_list=self.test_task_statuses,
            start=datetime.datetime(2013, 6, 20, 0, 0),
            end=datetime.datetime(2013, 6, 30, 0, 0),
            schedule_timing=10,
            schedule_unit='d',
            schedule_model='effort',
        )
        DBSession.add(self.test_task1)

        self.test_task2 = Task(
            name='Test Task 2',
            project=self.test_project1,
            status_list=self.test_task_statuses,
            start=datetime.datetime(2013, 6, 20, 0, 0),
            end=datetime.datetime(2013, 6, 30, 0, 0),
            schedule_timing=10,
            schedule_unit='d',
            schedule_model='effort',
        )
        DBSession.add(self.test_task2)

        self.test_task3 = Task(
            name='Test Task 3',
            project=self.test_project1,
            status_list=self.test_task_statuses,
            resources=[self.test_user1, self.test_user2],
            responsible=[self.test_user1, self.test_user2],
            start=datetime.datetime(2013, 6, 20, 0, 0),
            end=datetime.datetime(2013, 6, 30, 0, 0),
            schedule_timing=10,
            schedule_unit='d',
            schedule_model='effort',
        )
        DBSession.add(self.test_task3)

        # children tasks

        # children of self.test_task1
        self.test_task4 = Task(
            name='Test Task 4',
            parent=self.test_task1,
            status=self.status_wfd,
            status_list=self.test_task_statuses,
            resources=[self.test_user1],
            depends=[self.test_task3],
            start=datetime.datetime(2013, 6, 20, 0, 0),
            end=datetime.datetime(2013, 6, 30, 0, 0),
            schedule_timing=10,
            schedule_unit='d',
            schedule_model='effort',
        )
        DBSession.add(self.test_task4)

        self.test_task5 = Task(
            name='Test Task 5',
            parent=self.test_task1,
            status_list=self.test_task_statuses,
            resources=[self.test_user1],
            depends=[self.test_task4],
            start=datetime.datetime(2013, 6, 20, 0, 0),
            end=datetime.datetime(2013, 6, 30, 0, 0),
            schedule_timing=10,
            schedule_unit='d',
            schedule_model='effort',
        )
        DBSession.add(self.test_task5)

        self.test_task6 = Task(
            name='Test Task 6',
            parent=self.test_task1,
            status_list=self.test_task_statuses,
            resources=[self.test_user1],
            start=datetime.datetime(2013, 6, 20, 0, 0),
            end=datetime.datetime(2013, 6, 30, 0, 0),
            schedule_timing=10,
            schedule_unit='d',
            schedule_model='effort',
        )
        DBSession.add(self.test_task6)

        # children of self.test_task2
        self.test_task7 = Task(
            name='Test Task 7',
            parent=self.test_task2,
            status_list=self.test_task_statuses,
            resources=[self.test_user2],
            start=datetime.datetime(2013, 6, 20, 0, 0),
            end=datetime.datetime(2013, 6, 30, 0, 0),
            schedule_timing=10,
            schedule_unit='d',
            schedule_model='effort',
        )
        DBSession.add(self.test_task7)

        self.test_task8 = Task(
            name='Test Task 8',
            parent=self.test_task2,
            status_list=self.test_task_statuses,
            resources=[self.test_user2],
            start=datetime.datetime(2013, 6, 20, 0, 0),
            end=datetime.datetime(2013, 6, 30, 0, 0),
            schedule_timing=10,
            schedule_unit='d',
            schedule_model='effort',
        )
        DBSession.add(self.test_task8)

        self.test_asset_status_list = StatusList.query\
            .filter_by(target_entity_type='Asset').first()
        DBSession.add(self.test_asset_status_list)

        # create an asset in between
        from stalker import Asset
        self.test_asset1 = Asset(
            name='Test Asset 1',
            code='TA1',
            parent=self.test_task7,
            type=Type(
                name='Character',
                code='Char',
                target_entity_type='Asset',
            ),
            status_list=self.test_asset_status_list
        )
        DBSession.add(self.test_asset1)

        # new task under asset
        self.test_task9 = Task(
            name='Test Task 9',
            parent=self.test_asset1,
            status_list=self.test_task_statuses,
            start=datetime.datetime(2013, 6, 20, 0, 0),
            end=datetime.datetime(2013, 6, 30, 0, 0),
            resources=[self.test_user2],
            schedule_timing=10,
            schedule_unit='d',
            schedule_model='effort',
        )
        DBSession.add(self.test_task9)
        DBSession.commit()

        # --------------
        # Task Hierarchy
        # --------------
        #
        # +-> Test Task 1
        # |   |
        # |   +-> Test Task 4
        # |   |
        # |   +-> Test Task 5
        # |   |
        # |   +-> Test Task 6
        # |
        # +-> Test Task 2
        # |   |
        # |   +-> Test Task 7
        # |   |   |
        # |   |   +-> Test Asset 1
        # |   |       |
        # |   |       +-> Test Task 9
        # |   |
        # |   +-> Test Task 8
        # |
        # +-> Test Task 3

        # no children for self.test_task3
        self.all_tasks = [
            self.test_task1, self.test_task2, self.test_task3,
            self.test_task4, self.test_task5, self.test_task6,
            self.test_task7, self.test_task8, self.test_task9,
            self.test_asset1
        ]

    def test_walk_hierarchy_is_working_properly(self):
        """testing if walk_hierarchy_is_working_properly
        """
        # this test should not be placed here
        visited_tasks = []
        expected_result = [
            self.test_task2, self.test_task7, self.test_task8,
            self.test_asset1, self.test_task9
        ]

        for task in self.test_task2.walk_hierarchy():
            visited_tasks.append(task)

        self.assertEqual(expected_result, visited_tasks)

    def test_walk_dependencies_is_working_properly(self):
        """testing if walk_dependencies is working properly
        """
        # this test should not be placed here
        visited_tasks = []
        expected_result = [
            self.test_task9, self.test_task6, self.test_task4, self.test_task5,
            self.test_task8, self.test_task3, self.test_task4, self.test_task8,
            self.test_task3
        ]

        # setup dependencies
        self.test_task9.depends = [self.test_task6]
        self.test_task6.depends = [self.test_task4, self.test_task5]
        self.test_task5.depends = [self.test_task4]
        self.test_task4.depends = [self.test_task8, self.test_task3]

        for task in self.test_task9.walk_dependencies():
            visited_tasks.append(task)

        self.assertEqual(expected_result, visited_tasks)

    # The following tests will test the status changes in dependency changes

    # Leaf Tasks - dependency relation changes
    # WFD
    def test_leaf_WFD_task_updated_to_have_a_dependency_of_WFD_task_task(self):
        """testing if it is possible to set a dependency between a task with
        WFD status to a task with WFD status and the status of the task will
        stay WFD
        """
        # create another dependency to make the task3 a WFD task
        self.test_task3.depends = []
        self.test_task9.status = self.status_wip
        self.assertEqual(self.test_task9.status, self.status_wip)
        self.test_task3.depends.append(self.test_task9)
        self.assertEqual(self.test_task3.status, self.status_wfd)
        # make a task with HREV status
        # create dependency
        self.test_task8.status = self.status_wfd
        self.assertEqual(self.test_task8.status, self.status_wfd)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_WFD_task_updated_to_have_a_dependency_of_RTS_task(self):
        """testing if it is possible to set a dependency between a task with
        WFD status to a task with RTS status and the status of the task will
        stay WFD
        """
        # create another dependency to make the task3 a WFD task
        self.test_task3.depends = []
        self.test_task9.status = self.status_wip
        self.assertEqual(self.test_task9.status, self.status_wip)
        self.test_task3.depends.append(self.test_task9)
        self.assertEqual(self.test_task3.status, self.status_wfd)
        # make a task with HREV status
        # create dependency
        self.test_task8.status = self.status_rts
        self.assertEqual(self.test_task8.status, self.status_rts)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_WFD_task_updated_to_have_a_dependency_of_WIP_task(self):
        """testing if it is possible to set a dependency between a task with
        WFD status to a task with WIP status and the status of the task will
        stay WFD
        """
        # create another dependency to make the task3 a WFD task
        self.test_task3.depends = []
        self.test_task9.status = self.status_wip
        self.assertEqual(self.test_task9.status, self.status_wip)
        self.test_task3.depends.append(self.test_task9)
        self.assertEqual(self.test_task3.status, self.status_wfd)
        # make a task with HREV status
        # create dependency
        self.test_task8.status = self.status_wip
        self.assertEqual(self.test_task8.status, self.status_wip)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_WFD_task_updated_to_have_a_dependency_of_PREV_task(self):
        """testing if it is possible to set a dependency between a task with
        WFD status to a task with PREV status and the status of the task will
        stay WFD
        """
        # create another dependency to make the task3 a WFD task
        self.test_task3.depends = []
        self.test_task9.status = self.status_wip
        self.assertEqual(self.test_task9.status, self.status_wip)
        self.test_task3.depends.append(self.test_task9)
        self.assertEqual(self.test_task3.status, self.status_wfd)
        # make a task with HREV status
        # create dependency
        self.test_task8.status = self.status_prev
        self.assertEqual(self.test_task8.status, self.status_prev)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_WFD_task_updated_to_have_a_dependency_of_HREV_task(self):
        """testing if it is possible to set a dependency between a task with
        WFD status to a task with HREV status and the status of the task will
        stay WFD
        """
        # create another dependency to make the task3 a WFD task
        self.test_task3.depends = []
        self.test_task9.status = self.status_wip
        self.assertEqual(self.test_task9.status, self.status_wip)
        self.test_task3.depends.append(self.test_task9)
        self.assertEqual(self.test_task3.status, self.status_wfd)
        # make a task with HREV status
        # create dependency
        self.test_task8.status = self.status_hrev
        self.assertEqual(self.test_task8.status, self.status_hrev)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_WFD_task_updated_to_have_a_dependency_of_OH_task(self):
        """testing if it is possible to set a dependency between a task with
        WFD status to a task with OH status and the status of the task will
        stay WFD
        """
        # create another dependency to make the task3 a WFD task
        self.test_task3.depends = []
        self.test_task9.status = self.status_wip
        self.assertEqual(self.test_task9.status, self.status_wip)
        self.test_task3.depends.append(self.test_task9)
        self.assertEqual(self.test_task3.status, self.status_wfd)
        # make a task with HREV status
        # create dependency
        self.test_task8.status = self.status_oh
        self.assertEqual(self.test_task8.status, self.status_oh)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_WFD_task_updated_to_have_a_dependency_of_STOP_task(self):
        """testing if it is possible to set a dependency between a task with
        WFD status to a task with STOP status and the status of the task status
        will stay WFD
        """
        # create another dependency to make the task3 a WFD task
        self.test_task3.depends = []
        self.test_task9.status = self.status_wip
        self.assertEqual(self.test_task9.status, self.status_wip)
        self.test_task3.depends.append(self.test_task9)
        self.assertEqual(self.test_task3.status, self.status_wfd)
        # make a task with HREV status
        # create dependency
        self.test_task8.status = self.status_stop
        self.assertEqual(self.test_task8.status, self.status_stop)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_WFD_task_updated_to_have_a_dependency_of_CMPL_task(self):
        """testing if it is possible to set a dependency between a task with
        WFD status to a task with CMPL status and the status of the task status
        will stay to WFD
        """
        # create another dependency to make the task3 a WFD task
        self.test_task3.depends = []
        self.test_task9.status = self.status_wip
        self.assertEqual(self.test_task9.status, self.status_wip)
        self.test_task3.depends.append(self.test_task9)
        self.assertEqual(self.test_task3.status, self.status_wfd)
        # make a task with HREV status
        # create dependency
        self.test_task8.status = self.status_cmpl
        self.assertEqual(self.test_task8.status, self.status_cmpl)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    # Leaf Tasks - dependency relation changes
    # RTS
    def test_leaf_RTS_task_updated_to_have_a_dependency_of_WFD_task_task(self):
        """testing if it is possible to set a dependency between a task with
        RTS status to a task with WFD status but the status of the task is
        updated from RTS to WFD
        """
        # find an RTS task
        self.test_task3.depends = []
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        # make a task with WFD status
        self.test_task8.status = self.status_wfd
        self.assertEqual(self.test_task8.status, self.status_wfd)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_RTS_task_updated_to_have_a_dependency_of_RTS_task(self):
        """testing if it is possible to set a dependency between a task with
        RTS status to a task with RTS status but the status of the task is
        updated from RTS to WFD
        """
        # find an RTS task
        self.test_task3.depends = []
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        # make a task with RTS status
        self.test_task8.status = self.status_rts
        self.assertEqual(self.test_task8.status, self.status_rts)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_RTS_task_updated_to_have_a_dependency_of_WIP_task(self):
        """testing if it is possible to set a dependency between a task with
        RTS status to a task with WIP status but the status of the task is
        updated from RTS to WFD
        """
        # find an RTS task
        self.test_task3.depends = []
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        # make a task with WIP status
        self.test_task8.status = self.status_wip
        self.assertEqual(self.test_task8.status, self.status_wip)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_RTS_task_updated_to_have_a_dependency_of_PREV_task(self):
        """testing if it is possible to set a dependency between a task with
        RTS status to a task with PREV status but the status of the task is
        updated from RTS to WFD
        """
        # find an RTS task
        self.test_task3.depends = []
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        # make a task with PREV status
        self.test_task8.status = self.status_prev
        self.assertEqual(self.test_task8.status, self.status_prev)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_RTS_task_updated_to_have_a_dependency_of_HREV_task(self):
        """testing if it is possible to set a dependency between a task with
        RTS status to a task with HREV status but the status of the task is
        updated from RTS to WFD
        """
        # find an RTS task
        self.test_task3.depends = []
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        # make a task with HREV status
        self.test_task8.status = self.status_hrev
        self.assertEqual(self.test_task8.status, self.status_hrev)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_RTS_task_updated_to_have_a_dependency_of_OH_task(self):
        """testing if it is possible to set a dependency between a task with
        RTS status to a task with OH status and the status of the task is
        updated from RTS to WFD
        """
        # find an RTS task
        self.test_task3.depends = []
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        # make a task with OH status
        self.test_task8.status = self.status_oh
        self.assertEqual(self.test_task8.status, self.status_oh)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_leaf_RTS_task_updated_to_have_a_dependency_of_STOP_task(self):
        """testing if it is possible to set a dependency between a task with
        RTS status to a task with STOP status and the status of the task will
        stay RTS as if the dependency is not there
        """
        # find an RTS task
        self.test_task3.depends = []
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        # make a task with STOP status
        self.test_task8.status = self.status_stop
        self.assertEqual(self.test_task8.status, self.status_stop)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_rts)

    def test_leaf_RTS_task_updated_to_have_a_dependency_of_CMPL_task(self):
        """testing if it is possible to set a dependency between a task with
        RTS status to a task with CMPL status and the status of the task will
        stay RTS
        """
        # find an RTS task
        self.assertEqual(self.test_task3.depends, [])
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        # make a task with CMPL status
        self.test_task8.status = self.status_cmpl
        self.assertEqual(self.test_task8.status, self.status_cmpl)
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_rts)

    # Leaf Tasks - dependency changes
    # WIP - DREV - PREV - HREV - OH - STOP - CMPL
    def test_leaf_WIP_task_dependency_can_not_be_updated(self):
        """testing if it is not possible to update the dependencies of a WIP
        task
        """
        # find an WIP task
        self.test_task3.depends = []
        self.test_task3.status = self.status_wip
        self.assertEqual(self.test_task3.status, self.status_wip)
        # create dependency
        self.assertRaises(
            StatusError, self.test_task3.depends.append, self.test_task8
        )

    def test_leaf_PREV_task_dependency_can_not_be_updated(self):
        """testing if it is not possible to update the dependencies of a PREV
        task
        """
        # find an PREV task
        self.test_task3.depends = []
        self.test_task3.status = self.status_prev
        self.assertEqual(self.test_task3.status, self.status_prev)
        # create dependency
        self.assertRaises(
            StatusError, self.test_task3.depends.append, self.test_task8
        )

    def test_leaf_HREV_task_dependency_can_not_be_updated(self):
        """testing if it is not possible to update the dependencies of a HREV
        task
        """
        # find an HREV task
        self.test_task3.depends = []
        self.test_task3.status = self.status_hrev
        self.assertEqual(self.test_task3.status, self.status_hrev)
        # create dependency
        self.assertRaises(
            StatusError, self.test_task3.depends.append, self.test_task8
        )

    def test_leaf_DREV_task_dependency_can_not_be_updated(self):
        """testing if it is not possible to update the dependencies of a DREV
        task
        """
        # find an DREV task
        self.test_task3.depends = []
        self.test_task3.status = self.status_drev
        self.assertEqual(self.test_task3.status, self.status_drev)
        # create dependency
        self.assertRaises(
            StatusError, self.test_task3.depends.append, self.test_task8
        )

    def test_leaf_OH_task_dependency_can_not_be_updated(self):
        """testing if it is not possible to update the dependencies of a OH
        task
        """
        # find an OH task
        self.test_task3.depends = []
        self.test_task3.status = self.status_oh
        self.assertEqual(self.test_task3.status, self.status_oh)
        # create dependency
        self.assertRaises(
            StatusError, self.test_task3.depends.append, self.test_task8
        )

    def test_leaf_STOP_task_dependency_can_not_be_updated(self):
        """testing if it is not possible to update the dependencies of a STOP
        task
        """
        # find an STOP task
        self.test_task3.depends = []
        self.test_task3.status = self.status_stop
        self.assertEqual(self.test_task3.status, self.status_stop)
        # create dependency
        self.assertRaises(
            StatusError, self.test_task3.depends.append, self.test_task8
        )

    def test_leaf_CMPL_task_dependency_can_not_be_updated(self):
        """testing if it is not possible to update the dependencies of a CMPL
        task
        """
        # find an CMPL task
        self.test_task3.depends = []
        self.test_task3.status = self.status_cmpl
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        # create dependency
        self.assertRaises(
            StatusError, self.test_task3.depends.append, self.test_task8
        )

    # dependencies of containers
    # container Tasks - dependency relation changes
    # RTS
    def test_container_RTS_task_updated_to_have_a_dependency_of_WFD_task_task(self):
        """testing if it is possible to set a dependency between an RTS
        container task to a WFD task but the status of the container task is
        updated from RTS to WFD
        """
        # make a task with WFD status
        self.test_task3.depends = []
        self.test_task8.status = self.status_wfd
        self.assertEqual(self.test_task8.status, self.status_wfd)
        # find a RTS container task
        self.test_task3.children.append(self.test_task2)
        self.test_task2.status = self.status_rts
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_container_RTS_task_updated_to_have_a_dependency_of_RTS_task(self):
        """testing if it is possible to set a dependency between an RTS
        container task to an RTS task but the status of the container task is
        updated from RTS to WFD
        """
        # make a task with WFD status
        self.test_task3.depends = []
        self.test_task8.status = self.status_rts
        self.assertEqual(self.test_task8.status, self.status_rts)
        # find a RTS container task
        self.test_task3.children.append(self.test_task2)
        self.test_task2.status = self.status_rts
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_container_RTS_task_updated_to_have_a_dependency_of_WIP_task(self):
        """testing if it is possible to set a dependency between an RTS
        container task to a WIP task but the status of the container task is
        updated from RTS to WFD
        """
        # make a task with WIP status
        self.test_task3.depends = []
        self.test_task8.status = self.status_wip
        self.assertEqual(self.test_task8.status, self.status_wip)
        # find a RTS container task
        self.test_task3.children.append(self.test_task2)
        self.test_task2.status = self.status_rts
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_container_RTS_task_updated_to_have_a_dependency_of_PREV_task(self):
        """testing if it is possible to set a dependency between an RTS
        container task to a PREV task but the status of the container task is
        updated from RTS to WFD
        """
        # make a task with PREV status
        self.test_task3.depends = []
        self.test_task8.status = self.status_prev
        self.assertEqual(self.test_task8.status, self.status_prev)
        # find a RTS container task
        self.test_task3.children.append(self.test_task2)
        self.test_task2.status = self.status_rts
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_container_RTS_task_updated_to_have_a_dependency_of_HREV_task(self):
        """testing if it is possible to set a dependency between an RTS
        container task to an HREV task but the status of the container task is
        updated from RTS to WFD
        """
        # make a task with HREV status
        self.test_task3.depends = []
        self.test_task8.status = self.status_hrev
        self.assertEqual(self.test_task8.status, self.status_hrev)
        # find a RTS container task
        self.test_task3.children.append(self.test_task2)
        self.test_task2.status = self.status_rts
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_container_RTS_task_updated_to_have_a_dependency_of_OH_task(self):
        """testing if it is possible to set a dependency between an RTS
        container task to an OH task but the status of the container task is
        updated from RTS to WFD
        """
        # make a task with OH status
        self.test_task3.depends = []
        self.test_task8.status = self.status_oh
        self.assertEqual(self.test_task8.status, self.status_oh)
        # find a RTS container task
        self.test_task3.children.append(self.test_task2)
        self.test_task2.status = self.status_rts
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_wfd)

    def test_container_RTS_task_updated_to_have_a_dependency_of_STOP_task(self):
        """testing if it is possible to set a dependency between an RTS
        container task to a STOP task and the status of the container task will
        stay RTS as if the dependency is not there
        """
        # make a task with STOP status
        self.test_task3.depends = []
        self.test_task8.status = self.status_stop
        self.assertEqual(self.test_task8.status, self.status_stop)
        # find a RTS container task
        self.test_task3.children.append(self.test_task2)
        self.test_task2.status = self.status_rts
        self.test_task3.status = self.status_rts
        self.assertEqual(self.test_task3.status, self.status_rts)
        # create dependency
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_rts)

    def test_container_RTS_task_updated_to_have_a_dependency_of_CMPL_task(self):
        """testing if it is possible to set a dependency between an RTS
        container task to a CMPL task and the status of the task will stay RTS
        """
        # make a task with CMPL status
        self.test_task3.depends = []
        self.test_task3.children.append(self.test_task6)

        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()
        self.test_task8.create_time_log(
            resource=self.test_task8.resources[0],
            start=now,
            end=now + td(hours=1)
        )

        reviews = self.test_task8.request_review()
        for review in reviews:
            review.approve()

        self.assertEqual(self.test_task8.status, self.status_cmpl)

        # find a RTS container task
        self.assertEqual(self.test_task3.status, self.status_rts)

        # create dependency
        self.test_task3.depends.append(self.test_task8)
        self.assertEqual(self.test_task3.status, self.status_rts)

    # Container Tasks - dependency relation changes
    # WIP - DREV - PREV - HREV - OH - STOP - CMPL
    def test_container_WIP_task_dependency_can_not_be_updated(self):
        """testing if it is not possible to update the dependencies of a WIP
        container task
        """
        # find an WIP task
        self.test_task1.depends = []
        self.test_task1.status = self.status_wip
        self.assertEqual(self.test_task1.status, self.status_wip)
        # create dependency
        self.assertRaises(
            StatusError, self.test_task1.depends.append, self.test_task8
        )

    def test_container_CMPL_task_dependency_can_not_be_updated(self):
        """testing if it is not possible to update the dependencies of a CMPL
        container task
        """
        # find an CMPL task
        self.test_task1.status = self.status_cmpl
        self.assertEqual(self.test_task1.status, self.status_cmpl)
        # create dependency
        with DBSession.no_autoflush:
            self.assertRaises(
                StatusError, self.test_task1.depends.append, self.test_task8
            )

    #
    # Action Tests
    #

    # create_time_log
    # WFD
    def test_create_time_log_in_WFD_leaf_task(self):
        """testing if a StatusError will be raised when the the create_time_log
        actions is used in a WFD task
        """
        self.test_task3.status = self.status_wfd
        resource = self.test_task3.resources[0]
        start = datetime.datetime.now()
        end = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.assertRaises(StatusError, self.test_task3.create_time_log,
                          resource, start, end)

    # RTS: status updated to WIP
    def test_create_time_log_in_RTS_leaf_task_status_updated_to_WIP(self):
        """testing if the status of the RTS leaf task will be converted to WIP
        when create_time_log actions is used in an RTS task
        """
        self.test_task9.status = self.status_rts
        resource = self.test_task9.resources[0]
        start = datetime.datetime.now()
        end = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.test_task9.create_time_log(resource, start, end)
        self.assertEqual(self.test_task9.status, self.status_wip)

    # RTS -> parent update
    def test_create_time_log_in_RTS_leaf_task_update_parent_status(self):
        """testing if the status of the parent of the RTS leaf task will be
        converted to WIP when create_time_log actions is used in an RTS task
        """
        self.test_task2.status = self.status_rts
        self.test_task8.status = self.status_rts

        self.assertEqual(
            self.test_task8.parent, self.test_task2
        )

        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task8.create_time_log(
            resource=self.test_task8.resources[0],
            start=now,
            end=now + td(hours=1)
        )

        self.assertEqual(self.test_task8.status, self.status_wip)
        self.assertEqual(self.test_task2.status, self.status_wip)

    # RTS -> root task no problem
    def test_create_time_log_in_RTS_root_task_no_parent_no_problem(self):
        """testing if RTS leaf task status will be converted to WIP when
        create_time_log actions is used in an RTS root task
        """
        self.test_task3.status = self.status_rts
        resource = self.test_task3.resources[0]
        start = datetime.datetime.now()
        end = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.test_task3.create_time_log(resource, start, end)
        self.assertEqual(self.test_task3.status, self.status_wip)

    # WIP
    def test_create_time_log_in_WIP_leaf_task(self):
        """testing if there will be no problem when create_time_log is used
        in a WIP task, and the status will stay WIP
        """
        self.test_task9.status = self.status_wip
        resource = self.test_task9.resources[0]
        start = datetime.datetime.now()
        end = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.test_task9.create_time_log(resource, start, end)
        self.assertEqual(self.test_task9.status, self.status_wip)

    # PREV
    def test_create_time_log_in_PREV_leaf_task(self):
        """testing if a StatusError will be raised when create_time_log is used
        in a PREV task
        """
        self.test_task3.status = self.status_prev
        resource = self.test_task3.resources[0]
        start = datetime.datetime.now()
        end = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.assertRaises(StatusError, self.test_task3.create_time_log,
                          resource, start, end)

    # HREV
    def test_create_time_log_in_HREV_leaf_task(self):
        """testing if the status will be converted to WIP when create_time_log
        is used in a HREV task
        """
        self.test_task9.status = self.status_hrev
        resource = self.test_task9.resources[0]
        start = datetime.datetime.now()
        end = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.test_task9.create_time_log(resource, start, end)
        self.assertEqual(self.test_task9.status, self.status_wip)

    # DREV
    def test_create_time_log_in_DREV_leaf_task(self):
        """testing if the status will stay DREV when create_time_log is used in
        a DREV task
        """
        self.test_task9.status = self.status_drev
        resource = self.test_task9.resources[0]
        start = datetime.datetime.now()
        end = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.test_task9.create_time_log(resource, start, end)
        self.assertEqual(self.test_task9.status, self.status_drev)

    # OH
    def test_create_time_log_in_OH_leaf_task(self):
        """testing if a StatusError will be raised when the create_time_log
        actions is used in a OH task
        """
        self.test_task9.status = self.status_oh
        resource = self.test_task9.resources[0]
        start = datetime.datetime.now()
        end = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.assertRaises(StatusError, self.test_task9.create_time_log,
                          resource, start, end)

    # STOP
    def test_create_time_log_in_STOP_leaf_task(self):
        """testing if a StatusError will be raised when the create_time_log
        action is used in a STOP task
        """
        self.test_task9.status = self.status_stop
        resource = self.test_task9.resources[0]
        start = datetime.datetime.now()
        end = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.assertRaises(StatusError, self.test_task9.create_time_log,
                          resource, start, end)

    # CMPL
    def test_create_time_log_in_CMPL_leaf_task(self):
        """testing if a StatusError will be raised when the create_time_log
        action is used in a CMPL task
        """
        self.test_task9.status = self.status_cmpl
        resource = self.test_task9.resources[0]
        start = datetime.datetime.now()
        end = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.assertRaises(StatusError, self.test_task9.create_time_log,
                          resource, start, end)

    # On Container Task
    def test_create_time_log_on_container_task(self):
        """testing if a ValueError will be raised when the create_time_log
        action will be used in a container task
        """
        start = datetime.datetime.now()
        end = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.assertRaises(ValueError, self.test_task2.create_time_log,
                          resource=None, start=start, end=end)

    def test_create_time_log_is_creating_time_logs(self):
        """testing if create_time_log action is really creating some time logs
        """
        # initial condition
        self.assertEqual(len(self.test_task3.time_logs), 0)

        now = datetime.datetime.now()
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + datetime.timedelta(hours=1)
        )
        self.assertEqual(len(self.test_task3.time_logs), 1)
        self.assertEqual(self.test_task3.total_logged_seconds, 3600)

        now = datetime.datetime.now()
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + datetime.timedelta(hours=1),
            end=now + datetime.timedelta(hours=2)
        )
        self.assertEqual(len(self.test_task3.time_logs), 2)
        self.assertEqual(self.test_task3.total_logged_seconds, 7200)

    # request_review
    # WFD
    def test_request_review_in_WFD_leaf_task(self):
        """testing if a StatusError will be raised when the request_review
        action is used in a WFD leaf task
        """
        self.test_task3.status = self.status_wfd
        self.assertRaises(StatusError, self.test_task3.request_review)

    # RTS
    def test_request_review_in_RTS_leaf_task(self):
        """testing if a StatusError will be raised when the request_review
        action is used in a RTS leaf task
        """
        self.test_task3.status = self.status_rts
        self.assertRaises(StatusError, self.test_task3.request_review)

    # WIP: status updated to PREV
    def test_request_review_in_WIP_leaf_task_status_updated_to_PREV(self):
        """testing if the status will be updated to PREV when the
        request_review action is used in a WIP leaf task
        """
        self.test_task3.status = self.status_wip
        self.test_task3.request_review()
        self.assertEqual(self.test_task3.status, self.status_prev)

    # WIP: review instances
    def test_request_review_in_WIP_leaf_task_review_instances(self):
        """testing if a review instance for each responsible will be returned
        when the request_review action is used in a WIP leaf task
        """
        from stalker import Review
        self.test_task3.responsible = [self.test_user1, self.test_user2]
        self.test_task3.status = self.status_wip
        reviews = self.test_task3.request_review()
        self.assertEqual(len(reviews), 2)
        self.assertIsInstance(reviews[0], Review)
        self.assertIsInstance(reviews[1], Review)

    # WIP: review instances review_number is correct
    def test_request_review_in_WIP_leaf_task_review_instances_review_number(self):
        """testing if the review_number attribute of the created Reviews are
        correctly set
        """
        self.test_task3.responsible = [self.test_user1, self.test_user2]
        self.test_task3.status = self.status_wip

        # request a review
        reviews = self.test_task3.request_review()
        review1 = reviews[0]
        review2 = reviews[1]
        self.assertEqual(review1.review_number, 1)
        self.assertEqual(review2.review_number, 1)

        # finalize reviews
        review1.approve()
        review2.approve()

        # request a revision
        review3 = self.test_task3.request_revision(
            reviewer=self.test_user1,
            description='some description',
            schedule_timing=1,
            schedule_unit='d'
        )

        # the new_review.revision number still should be 1
        self.assertEqual(
            review3.review_number, 2
        )

        # and then ask a review again
        self.test_task3.status = self.status_wip

        reviews = self.test_task3.request_review()
        self.assertEqual(reviews[0].review_number, 3)
        self.assertEqual(reviews[1].review_number, 3)

    # PREV
    def test_request_review_in_PREV_leaf_task(self):
        """testing if a StatusError will be raised when the request_review
        action is used in a PREV leaf task
        """
        self.test_task3.status = self.status_prev
        self.assertRaises(StatusError, self.test_task3.request_review)

    # HREV
    def test_request_review_in_HREV_leaf_task(self):
        """testing if a StatusError will be raised when the request_review
        action is used in a HREV leaf task
        """
        self.test_task3.status = self.status_hrev
        self.assertRaises(StatusError, self.test_task3.request_review)

    # DREV
    def test_request_review_in_DREV_leaf_task(self):
        """testing if a StatusError will be raised when the request_review
        action is used in a DREV leaf task
        """
        self.test_task3.status = self.status_drev
        self.assertRaises(StatusError, self.test_task3.request_review)

    # OH
    def test_request_review_in_OH_leaf_task(self):
        """testing if a StatusError will be raised when the request_review
        action is used in a OH leaf task
        """
        self.test_task3.status = self.status_oh
        self.assertRaises(StatusError, self.test_task3.request_review)

    # STOP
    def test_request_review_in_STOP_leaf_task(self):
        """testing if a StatusError will be raised when the request_review
        action is used in a STOP leaf task
        """
        self.test_task3.status = self.status_stop
        self.assertRaises(StatusError, self.test_task3.request_review)

    # CMPL
    def test_request_review_in_CMPL_leaf_task(self):
        """testing if a StatusError will be raised when the request_review
        action is used in a CMPL leaf task
        """
        self.test_task3.status = self.status_cmpl
        self.assertRaises(StatusError, self.test_task3.request_review)

    #request_revision
    #WFD
    def test_request_revision_in_WFD_leaf_task(self):
        """testing if a StatusError will be raised when the request_revision
        action is used in a WFD leaf task
        """
        self.test_task3.status = self.status_wfd
        self.assertRaises(StatusError, self.test_task3.request_revision)

    #RTS
    def test_request_revision_in_RTS_leaf_task(self):
        """testing if a StatusError will be raised when the request_revision
        action is used in a RTS leaf task
        """
        self.test_task3.status = self.status_rts
        self.assertRaises(StatusError, self.test_task3.request_revision)

    #WIP
    def test_request_revision_in_WIP_leaf_task(self):
        """testing if a StatusError will be raised when the request_revision
        action is used in a WIP leaf task
        """
        self.test_task3.status = self.status_wip
        self.assertRaises(StatusError, self.test_task3.request_revision)

    #PREV: Status updated to HREV
    def test_request_revision_in_PREV_leaf_task_status_updated_to_HREV(self):
        """testing if a the status of the PREV leaf task will be converted to
        HREV when the request_revision action is used in a PREV leaf task
        """
        self.test_task3.status = self.status_prev

        reviewer=self.test_user1
        description = 'do something uleyn'
        schedule_timing = 4
        schedule_unit = 'h'

        self.test_task3.request_revision(
            reviewer=reviewer,
            description=description,
            schedule_timing=schedule_timing,
            schedule_unit=schedule_unit
        )
        self.assertEqual(self.test_task3.status, self.status_hrev)

    #PREV: Schedule info update
    def test_request_revision_in_PREV_leaf_task_timing_is_extended(self):
        """testing if the timing will be extended as stated in the action when
        the request_revision action is used in a PREV leaf task
        """
        self.test_task3.status = self.status_prev

        reviewer = self.test_user1
        description = 'do something uleyn'
        schedule_timing = 4
        schedule_unit = 'h'

        self.test_task3.request_revision(
            reviewer=reviewer,
            description=description,
            schedule_timing=schedule_timing,
            schedule_unit=schedule_unit
        )
        self.assertEqual(self.test_task3.schedule_timing, 4)
        self.assertEqual(self.test_task3.schedule_unit, 'h')

    #PREV: Schedule info update also consider RREV Reviews
    def test_request_revision_in_PREV_leaf_task_schedule_info_update_also_considers_other_RREV_reviews_with_same_review_number(self):
        """testing if the timing values are extended with the supplied values
        and also any RREV Review timings with the same revision number are
        included when the request_revision action is used in a PREV leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task3.status = self.status_rts
        self.test_task3.responsible = [self.test_user1, self.test_user2]

        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        # check the status
        self.assertEqual(self.test_task3.status, self.status_wip)

        # first request a review
        reviews = self.test_task3.request_review()

        # only finalize the first review
        review1 = reviews[0]
        review2 = reviews[1]

        review1.request_revision(
            schedule_timing=6, schedule_unit='h', description=''
        )

        # now request_revision using the task
        review3 = self.test_task3.request_revision(
            reviewer=self.test_user1,
            description='do something uleyn',
            schedule_timing=4,
            schedule_unit='h'
        )
        self.assertEqual(
            len(self.test_task3.reviews), 2
        )

        # check if they are in the same review set
        self.assertEqual(
            review1.review_number, review3.review_number
        )

        # the final timing should be 12 hours
        self.assertEqual(self.test_task3.schedule_timing, 12)
        self.assertEqual(self.test_task3.schedule_unit, 'h')

    #PREV: Review instances statuses are updated
    def test_request_revision_in_PREV_leaf_task_review_instances_are_deleted(self):
        """testing if the NEW Review instances are deleted when the
        request_revision action is used in a PREV leaf task
        """
        self.test_task3.status = self.status_wip

        reviews = self.test_task3.request_review()
        review1 = reviews[0]
        review2 = reviews[1]

        review3 = self.test_task3.request_revision(
            reviewer=self.test_user2,
            description='some description',
            schedule_timing=4,
            schedule_unit='h'
        )

        # now check if the review instances are not in task3.reviews list
        # anymore
        self.assertNotIn(review1, self.test_task3.reviews)
        self.assertNotIn(review2, self.test_task3.reviews)
        self.assertIn(review3, self.test_task3.reviews)

    #PREV: Review instances statuses are updated
    def test_request_revision_in_PREV_leaf_task_new_review_instance_is_created(self):
        """testing if the statuses of review instances are correctly updated to
        RREV when the request_revision action is used in a PREV leaf task
        """
        self.test_task3.status = self.status_wip

        reviews = self.test_task3.request_review()
        new_review = self.test_task3.request_revision(
            reviewer=self.test_user2,
            description='some description',
            schedule_timing=1,
            schedule_unit='w'
        )
        from stalker import Review
        self.assertIsInstance(new_review, Review)

    #HREV
    def test_request_revision_in_HREV_leaf_task(self):
        """testing if a StatusError will be raised when the request_revision
        action is used in a HREV leaf task
        """
        self.test_task3.status = self.status_hrev
        kw = {
            'reviewer': self.test_user1,
            'description': 'do something uleyn',
            'schedule_timing': 4,
            'schedule_unit': 'h'
        }
        self.assertRaises(StatusError, self.test_task3.request_revision, **kw)

    #OH
    def test_request_revision_in_OH_leaf_task(self):
        """testing if a StatusError will be raised when the request_revision
        action is used in a OH leaf task
        """
        self.test_task3.status = self.status_oh
        kw = {
            'reviewer': self.test_user1,
            'description': 'do something uleyn',
            'schedule_timing': 4,
            'schedule_unit': 'h'
        }
        self.assertRaises(StatusError, self.test_task3.request_revision, **kw)

    #STOP
    def test_request_revision_in_STOP_leaf_task(self):
        """testing if a StatusError will be raised when the request_revision
        action is used in a STOP leaf task
        """
        self.test_task3.status = self.status_stop
        kw = {
            'reviewer': self.test_user1,
            'description': 'do something uleyn',
            'schedule_timing': 4,
            'schedule_unit': 'h'
        }
        self.assertRaises(StatusError, self.test_task3.request_revision, **kw)

    #CMPL: status update
    def test_request_revision_in_CMPL_leaf_task_status_updated_to_HREV(self):
        """testing if the status will be set to HREV and the timing values are
        extended with the supplied values when the request_revision action is
        used in a CMPL leaf task
        """
        self.test_task3.status = self.status_cmpl
        kw = {
            'reviewer': self.test_user1,
            'description': 'do something uleyn',
            'schedule_timing': 4,
            'schedule_unit': 'h'
        }
        review = self.test_task3.request_revision(**kw)
        self.assertEqual(self.test_task3.status, self.status_hrev)

    #CMPL: schedule info update
    def test_request_revision_in_CMPL_leaf_task_schedule_info_update(self):
        """testing if the timing values are extended with the supplied values
        when the request_revision action is used in a CMPL leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task3.status = self.status_rts
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )
        self.assertEqual(self.test_task3.total_logged_seconds, 7200)

        reviews = self.test_task3.request_review()
        review1 = reviews[0]
        review2 = reviews[1]
        review1.approve()
        review2.approve()

        kw = {
            'reviewer': self.test_user1,
            'description': 'do something uleyn',
            'schedule_timing': 4,
            'schedule_unit': 'h'
        }
        review3 = self.test_task3.request_revision(**kw)
        self.assertEqual(self.test_task3.schedule_unit, 'h')
        self.assertEqual(self.test_task3.schedule_timing, 6)

    #CMPL: parent status update
    def test_request_revision_in_CMPL_leaf_task_parent_status_updated_to_WIP(self):
        """testing if the status of the parent will be set to WIP when the
        request_revision action is used in a CMPL leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task9.status = self.status_rts
        TimeLog(
            task=self.test_task9,
            resource=self.test_task9.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        TimeLog(
            task=self.test_task9,
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        self.test_task9.status = self.status_cmpl
        self.test_asset1.status = self.status_cmpl

        kw = {
            'reviewer': self.test_user1,
            'description': 'do something uleyn',
            'schedule_timing': 4,
            'schedule_unit': 'h'
        }
        review = self.test_task9.request_revision(**kw)
        self.assertEqual(self.test_asset1.status, self.status_wip)

    #CMPL: dependent task status update RTS -> WFD
    def test_request_revision_in_CMPL_leaf_task_RTS_dependent_task_updated_to_WFD(self):
        """testing if the status of the dependent RTS task will be set to WFD
        when the request_revision action is used in a CMPL leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task8.depends = [self.test_task9]
        self.test_task8.status = self.status_wfd

        self.test_task9.status = self.status_rts
        TimeLog(
            task=self.test_task9,
            resource=self.test_task9.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        TimeLog(
            task=self.test_task9,
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        self.test_task9.status = self.status_cmpl

        kw = {
            'reviewer': self.test_user1,
            'description': 'do something uleyn',
            'schedule_timing': 4,
            'schedule_unit': 'h',
        }
        review = self.test_task9.request_revision(**kw)
        self.assertEqual(self.test_task8.status, self.status_wfd)

    #CMPL: dependent task status update WIP -> DREV
    def test_request_revision_in_CMPL_leaf_task_WIP_dependent_task_updated_to_DREV(self):
        """testing if the status of the dependent WIP task will be set to DREV
        when the request_revision action is used in a CMPL leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task8.depends = [self.test_task9]
        self.test_task8.status = self.status_wip

        self.test_task9.status = self.status_rts
        TimeLog(
            task=self.test_task9,
            resource=self.test_task9.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        TimeLog(
            task=self.test_task9,
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        self.test_task9.status = self.status_cmpl

        kw = {
            'reviewer': self.test_user1,
            'description': 'do something uleyn',
            'schedule_timing': 4,
            'schedule_unit': 'h'
        }
        review = self.test_task9.request_revision(**kw)
        self.assertEqual(self.test_task8.status, self.status_drev)

    #CMPL: dependent task status update CMPL -> DREV
    def test_request_revision_in_CMPL_leaf_task_CMPL_dependent_task_updated_to_DREV(self):
        """testing if the status of the dependent CMPL task will be set to DREV
        when the request_revision action is used in a CMPL leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task8.depends = [self.test_task9]
        self.assertIn(self.test_task9, self.test_task8.depends)

        self.test_task9.status = self.status_rts
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        reviews = self.test_task9.request_review()
        for r in reviews:
            r.approve()
        self.assertEqual(self.test_task9.status, self.status_cmpl)
        self.assertEqual(self.test_task8.status, self.status_rts)

        self.test_task8.create_time_log(
            resource=self.test_task8.resources[0],
            start=now + td(hours=2),
            end=now + td(hours=3)
        )
        self.assertEqual(self.test_task8.status, self.status_wip)

        [r.approve() for r in self.test_task8.request_review()]
        self.assertEqual(self.test_task8.status, self.status_cmpl)

        kw = {
            'reviewer': self.test_user1,
            'description': 'do something uleyn',
            'schedule_timing': 4,
            'schedule_unit': 'h'
        }
        self.test_task9.request_revision(**kw)

        self.assertEqual(self.test_task9.status, self.status_hrev)
        self.assertEqual(self.test_task8.status, self.status_drev)

    #CMPL: dependent task dependency_target update CMPL -> DREV
    def test_request_revision_in_CMPL_leaf_task_CMPL_dependent_task_dependency_target_updated_to_onstart(self):
        """testing if the dependency_target attribute of the TaskDependency
        object between the revised task and the dependent CMPL task will be set
        to 'onstart' when the request_revision action is used in a CMPL leaf
        task
        """
        # create a couple of TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()


        self.test_task3.depends = [self.test_task9]  # will be PREV
        self.test_task4.depends = [self.test_task9]  # will be HREV
        self.test_task5.depends = [self.test_task9]  # will be STOP
        self.test_task6.depends = [self.test_task9]  # will be OH
        self.test_task8.depends = [self.test_task9]  # will be DREV
        self.assertIn(self.test_task9, self.test_task5.depends)
        self.assertIn(self.test_task9, self.test_task6.depends)
        self.assertIn(self.test_task9, self.test_task8.depends)

        self.test_task9.status = self.status_rts
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        reviews = self.test_task9.request_review()
        for r in reviews:
            r.approve()
        self.assertEqual(self.test_task9.status, self.status_cmpl)
        self.assertEqual(self.test_task8.status, self.status_rts)

        self.test_task8.create_time_log(
            resource=self.test_task8.resources[0],
            start=now + td(hours=2),
            end=now + td(hours=3)
        )
        self.assertEqual(self.test_task8.status, self.status_wip)

        [r.approve() for r in self.test_task8.request_review()]
        self.assertEqual(self.test_task8.status, self.status_cmpl)

        # now work on task5
        self.test_task5.create_time_log(
            resource=self.test_task5.resources[0],
            start=now + td(hours=3),
            end=now + td(hours=4)
        )
        self.assertEqual(self.test_task5.status, self.status_wip)
        self.test_task5.hold()
        self.assertEqual(self.test_task5.status, self.status_oh)

        # now work on task6
        self.test_task6.create_time_log(
            resource=self.test_task6.resources[0],
            start=now + td(hours=4),
            end=now + td(hours=5)
        )
        self.assertEqual(self.test_task6.status, self.status_wip)
        self.test_task6.stop()
        self.assertEqual(self.test_task6.status, self.status_stop)

        # now work on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + td(hours=5),
            end=now + td(hours=6)
        )
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.test_task3.request_review()
        self.assertEqual(self.test_task3.status, self.status_prev)

        # now work on task4
        self.test_task4.create_time_log(
            resource=self.test_task4.resources[0],
            start=now + td(hours=6),
            end=now + td(hours=7)
        )
        self.assertEqual(self.test_task4.status, self.status_wip)
        reviews = self.test_task4.request_review()
        self.assertEqual(self.test_task4.status, self.status_prev)
        for r in reviews:
            r.request_revision(
                schedule_timing=1,
                schedule_unit='h'
            )
        self.assertEqual(self.test_task4.status, self.status_hrev)

        kw = {
            'reviewer': self.test_user1,
            'description': 'do something uleyn',
            'schedule_timing': 4,
            'schedule_unit': 'h'
        }
        self.test_task9.request_revision(**kw)

        from stalker import TaskDependency
        tdep_t3 = TaskDependency.query\
            .filter_by(task=self.test_task3)\
            .filter_by(depends_to=self.test_task9)\
            .first()
        tdep_t4 = TaskDependency.query\
            .filter_by(task=self.test_task4)\
            .filter_by(depends_to=self.test_task9)\
            .first()
        tdep_t5 = TaskDependency.query\
            .filter_by(task=self.test_task5)\
            .filter_by(depends_to=self.test_task9)\
            .first()
        tdep_t6 = TaskDependency.query\
            .filter_by(task=self.test_task6)\
            .filter_by(depends_to=self.test_task9)\
            .first()
        tdep_t8 = TaskDependency.query\
            .filter_by(task=self.test_task8)\
            .filter_by(depends_to=self.test_task9)\
            .first()
        self.assertIsNotNone(tdep_t3)
        self.assertIsNotNone(tdep_t4)
        self.assertIsNotNone(tdep_t5)
        self.assertIsNotNone(tdep_t6)
        self.assertIsNotNone(tdep_t8)
        self.assertEqual(tdep_t3.dependency_target, 'onstart')
        self.assertEqual(tdep_t4.dependency_target, 'onstart')
        self.assertEqual(tdep_t5.dependency_target, 'onstart')
        self.assertEqual(tdep_t6.dependency_target, 'onstart')
        self.assertEqual(tdep_t8.dependency_target, 'onstart')

    #CMPL: dependent task parent status updated to WIP
    def test_request_revision_in_CMPL_leaf_task_dependent_task_parent_status_updated_to_WIP(self):
        """testing if the status of the dependent task parent updated to WIP
        when the request_revision action is used in a CMPL leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task9.depends = [self.test_task8]
        self.test_task9.status = self.status_wfd
        self.test_asset1.status = self.status_wfd
        self.test_task8.status = self.status_rts

        self.test_task8.create_time_log(
            resource=self.test_task8.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        self.test_task8.create_time_log(
            resource=self.test_task8.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        self.test_task8.status = self.status_cmpl
        self.test_task9.status = self.status_cmpl
        self.test_asset1.status = self.status_cmpl
        self.test_task7.status = self.status_cmpl

        kw = {
            'reviewer': self.test_user1,
            'description': 'do something uleyn',
            'schedule_timing': 4,
            'schedule_unit': 'h'
        }
        review = self.test_task8.request_revision(**kw)

        self.assertEqual(self.test_task9.status, self.status_drev)
        self.assertEqual(self.test_asset1.status, self.status_wip)
        self.assertEqual(self.test_task7.status, self.status_wip)

    # hold
    # WFD
    def test_hold_in_WFD_leaf_task(self):
        """testing if a StatusError will be raised when the hold action is used
        in a WFD leaf task
        """
        self.test_task3.status = self.status_wfd
        self.assertRaises(StatusError, self.test_task3.hold)

    # RTS
    def test_hold_in_RTS_leaf_task(self):
        """testing if a StatusError will be raised when the hold action is used
        in a RTS leaf task
        """
        self.test_task3.status = self.status_rts
        self.assertRaises(StatusError, self.test_task3.hold)

    # WIP: Status updated to OH
    def test_hold_in_WIP_leaf_task_status(self):
        """testing if the status will be updated to OH when the hold action is
        used in a WIP leaf task
        """
        self.test_task3.status = self.status_wip
        self.test_task3.hold()
        self.assertEqual(self.test_task3.status, self.status_oh)

    # WIP: Schedule values are intact
    def test_hold_in_WIP_leaf_task_schedule_values(self):
        """testing if the schedule values will be intact when the hold action
        is used in a WIP leaf task
        """
        self.test_task3.status = self.status_wip
        self.test_task3.hold()
        self.assertEqual(self.test_task3.schedule_timing, 10)
        self.assertEqual(self.test_task3.schedule_unit, 'd')

    # WIP: Priority is set to 0
    def test_hold_in_WIP_leaf_task(self):
        """testing if the priority will be set to 0 when the hold action is
        used in a WIP leaf task
        """
        self.test_task3.status = self.status_wip
        self.test_task3.hold()
        self.assertEqual(self.test_task3.priority, 0)

    # PREV
    def test_hold_in_PREV_leaf_task(self):
        """testing if a StatusError will be raised when the hold action is used
        in a PREV leaf task
        """
        self.test_task3.status = self.status_prev
        self.assertRaises(StatusError, self.test_task3.hold)

    # HREV
    def test_hold_in_HREV_leaf_task(self):
        """testing if a StatusError will be raised when the hold action is used
        in a HREV leaf task
        """
        self.test_task3.status = self.status_hrev
        self.assertRaises(StatusError, self.test_task3.hold)

    # DREV: Status updated to OH
    def test_hold_in_DREV_leaf_task_status_updated_to_OH(self):
        """testing if the status will be updated to OH when the hold action is
        used in a DREV leaf task
        """
        self.test_task3.status = self.status_drev
        self.test_task3.hold()
        self.assertEqual(self.test_task3.status, self.status_oh)

    # DREV: Schedule values are intact
    def test_hold_in_DREV_leaf_task_schedule_values_are_intact(self):
        """testing if the schedule values will be intact when the hold action
        is used in a DREV leaf task
        """
        self.test_task3.status = self.status_drev
        self.test_task3.hold()
        self.assertEqual(self.test_task3.schedule_timing, 10)
        self.assertEqual(self.test_task3.schedule_unit, 'd')

    # DREV: Priority is set to 0
    def test_hold_in_DREV_leaf_task_priority_set_to_0(self):
        """testing if the priority will be set to 0 when the hold action is
        used in a DREV leaf task
        """
        self.test_task3.status = self.status_drev
        self.test_task3.hold()
        self.assertEqual(self.test_task3.priority, 0)

    # OH
    def test_hold_in_OH_leaf_task(self):
        """testing if the status will stay on OH when the hold action is used
        in a OH leaf task
        """
        self.test_task3.status = self.status_oh
        self.test_task3.hold()
        self.assertEqual(self.test_task3.status, self.status_oh)

    # STOP
    def test_hold_in_STOP_leaf_task(self):
        """testing if a StatusError will be raised when the hold action is used
        in a STOP leaf task
        """
        self.test_task3.status = self.status_stop
        self.assertRaises(StatusError, self.test_task3.hold)

    # CMPL
    def test_hold_in_CMPL_leaf_task(self):
        """testing if a StatusError will be raised when the hold action is used
        in a CMPL leaf task
        """
        self.test_task3.status = self.status_cmpl
        self.assertRaises(StatusError, self.test_task3.hold)

    # stop
    # WFD
    def test_stop_in_WFD_leaf_task(self):
        """testing if a StatusError will be raised when the stop action is used
        in a WFD leaf task
        """
        self.test_task3.status = self.status_wfd
        self.assertRaises(StatusError, self.test_task3.stop)

    # RTS
    def test_stop_in_RTS_leaf_task(self):
        """testing if a StatusError will be raised when the stop action is used
        in a RTS leaf task
        """
        self.test_task3.status = self.status_rts
        self.assertRaises(StatusError, self.test_task3.stop)

    # WIP: Status Test
    def test_stop_in_WIP_leaf_task_status_is_updated_to_STOP(self):
        """testing if a status will be updated to STOP when the stop action is
        used in a WIP leaf task
        """
        self.test_task3.status = self.status_wip
        self.test_task3.hold()
        self.assertEqual(self.test_task3.status, self.status_oh)

    # WIP: Schedule Timing Test
    def test_stop_in_WIP_leaf_task_schedule_values_clamped(self):
        """testing if the schedule values will be clamped to the current
        total_logged_seconds when the stop action is used in a WIP leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task8.status = self.status_rts
        TimeLog(
            task=self.test_task8,
            resource=self.test_task8.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        TimeLog(
            task=self.test_task8,
            resource=self.test_task8.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )
        self.test_task8.status = self.status_wip
        self.test_task8.stop()
        self.assertEqual(self.test_task8.schedule_timing, 2)
        self.assertEqual(self.test_task8.schedule_unit, 'h')

    # WIP: Dependency Status: WFD -> RTS
    def test_stop_in_WIP_leaf_task_dependent_task_status_updated_from_WFD_to_RTS(self):
        """testing if the dependent task status updated from WFD to RTS when
        the stop action is used in a WIP leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task9.status = self.status_rts
        self.test_task8.status = self.status_rts

        self.test_task9.depends = [self.test_task8]

        TimeLog(
            task=self.test_task8,
            resource=self.test_task8.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        TimeLog(
            task=self.test_task8,
            resource=self.test_task8.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )
        self.test_task8.status = self.status_wip
        self.test_task8.stop()
        self.assertEqual(self.test_task9.status, self.status_rts)

    # WIP: Dependency Status: DREV -> WIP
    def test_stop_in_WIP_leaf_task_status_from_DREV_to_WIP(self):
        """testing if the dependent task status updated from DREV to WIP when
        the stop action is used in a WIP leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task9.status = self.status_rts
        self.test_task8.status = self.status_cmpl

        self.test_task9.depends = [self.test_task8]

        TimeLog(
            task=self.test_task9,
            resource=self.test_task9.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        TimeLog(
            task=self.test_task9,
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )
        self.test_task9.status = self.status_wip

        self.test_task8.status = self.status_hrev
        self.test_task9.status = self.status_drev

        TimeLog(
            task=self.test_task8,
            resource=self.test_task8.resources[0],
            start=now + td(hours=2),
            end=now + td(hours=3)
        )
        TimeLog(
            task=self.test_task8,
            resource=self.test_task8.resources[0],
            start=now + td(hours=4),
            end=now + td(hours=5)
        )

        self.test_task8.status = self.status_wip
        self.test_task8.stop()
        self.assertEqual(self.test_task9.status, self.status_wip)

    # WIP: parent statuses
    def test_stop_in_DREV_leaf_task_check_parent_status(self):
        """testing if the parent status is updated correctly when the stop
        action is used in a DREV leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        TimeLog(
            task=self.test_task9,
            resource=self.test_task9.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        TimeLog(
            task=self.test_task8,
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        self.test_task9.status = self.status_drev
        self.test_task9.stop()
        self.assertEqual(self.test_task9.status, self.status_stop)
        self.assertEqual(self.test_asset1.status, self.status_cmpl)

    # PREV
    def test_stop_in_PREV_leaf_task(self):
        """testing if a StatusError will be raised when the stop action is used
        in a PREV leaf task
        """
        self.test_task3.status = self.status_prev
        self.assertRaises(StatusError, self.test_task3.stop)

    # HREV
    def test_stop_in_HREV_leaf_task(self):
        """testing if a StatusError will be raised when the stop action is used
        in a HREV leaf task
        """
        self.test_task3.status = self.status_hrev
        self.assertRaises(StatusError, self.test_task3.stop)

    # DREV: Status Test
    def test_stop_in_DREV_leaf_task_status_is_updated_to_STOP(self):
        """testing if the status will be set to STOP when the stop action is
        used in a DREV leaf task
        """
        self.test_task3.status = self.status_drev
        self.test_task3.stop()
        self.assertEquals(self.test_task3.status, self.status_stop)

    # DREV: Schedule Timing Test
    def test_stop_in_DREV_leaf_task_schedule_values_are_clamped(self):
        """testing if the schedule timing value will be clamped to the current
        time logs when the stop action is used in a DREV leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task8.status = self.status_rts
        TimeLog(
            task=self.test_task8,
            resource=self.test_task8.resources[0],
            start=now,
            end=now + td(hours=2)
        )
        TimeLog(
            task=self.test_task8,
            resource=self.test_task8.resources[0],
            start=now + td(hours=2),
            end=now + td(hours=4)
        )
        self.test_task8.status = self.status_drev
        self.test_task8.stop()
        self.assertEqual(self.test_task8.schedule_timing, 4)
        self.assertEqual(self.test_task8.schedule_unit, 'h')

    # DREV: parent statuses
    def test_stop_in_DREV_leaf_task_parent_status(self):
        """testing if the parent status is updated correctly when the stop
        action is used in a DREV leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        TimeLog(
            task=self.test_task9,
            resource=self.test_task9.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        TimeLog(
            task=self.test_task8,
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        self.test_task9.status = self.status_wip
        self.test_task9.stop()
        self.assertEqual(self.test_task9.status, self.status_stop)
        self.assertEqual(self.test_asset1.status, self.status_cmpl)

    # DREV: Dependency Status: WFD -> RTS
    def test_stop_in_DREV_leaf_task_dependent_task_status_updated_from_WFD_to_RTS(self):
        """testing if the dependent task statuses are updated correctly when
        the stop action is used in a DREV leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task9.status = self.status_rts
        self.test_task8.status = self.status_rts

        self.test_task9.depends = [self.test_task8]

        TimeLog(
            task=self.test_task8,
            resource=self.test_task8.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        TimeLog(
            task=self.test_task8,
            resource=self.test_task8.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )
        self.test_task8.status = self.status_wip
        self.test_task8.stop()
        self.assertEqual(self.test_task9.status, self.status_rts)

    # DREV: Dependency Status: DREV -> WIP
    def test_stop_in_DREV_leaf_task_dependent_task_status_updated_from_DREV_to_WIP(self):
        """testing if the dependent task statuses are updated correctly when
        the stop action is used in a DREV leaf task
        """
        # create a couple TimeLogs
        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        self.test_task9.status = self.status_rts
        self.test_task8.status = self.status_rts

        self.test_task9.depends = [self.test_task8]
        self.test_task9.status = self.status_drev  # this will be set by an
                                                   # action in normal run
        TimeLog(
            task=self.test_task8,
            resource=self.test_task8.resources[0],
            start=now,
            end=now + td(hours=1)
        )
        TimeLog(
            task=self.test_task8,
            resource=self.test_task8.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )
        self.test_task8.status = self.status_wip
        self.test_task8.stop()
        self.assertEqual(self.test_task9.status, self.status_wip)

    # OH
    def test_stop_in_OH_leaf_task(self):
        """testing if a StatusError will be raised when the stop action is used
        in a OH leaf task
        """
        self.test_task3.status = self.status_oh
        self.assertRaises(StatusError, self.test_task3.stop)

    # STOP
    def test_stop_in_STOP_leaf_task(self):
        """testing if the status will stay on STOP when the stop action is used
        in a STOP leaf task
        """
        self.test_task3.status = self.status_stop
        self.test_task3.stop()
        self.assertEquals(self.test_task3.status, self.status_stop)

    # CMPL
    def test_stop_in_CMPL_leaf_task(self):
        """testing if a StatusError will be raised when the stop action is used
        in a CMPL leaf task
        """
        self.test_task3.status = self.status_cmpl
        self.assertRaises(StatusError, self.test_task3.stop)

    # resume
    # WFD
    def test_resume_in_WFD_leaf_task(self):
        """testing if a StatusError will be raised when the resume action is
        used in a WFD leaf task
        """
        self.test_task3.status = self.status_wfd
        self.assertRaises(StatusError, self.test_task3.resume)

    # RTS
    def test_resume_in_RTS_leaf_task(self):
        """testing if a StatusError will be raised when the resume action is
        used in a RTS leaf task
        """
        self.test_task3.status = self.status_rts
        self.assertRaises(StatusError, self.test_task3.resume)

    # WIP
    def test_resume_in_WIP_leaf_task(self):
        """testing if a StatusError will be raised when the resume action is
        used in a WIP leaf task
        """
        self.test_task3.status = self.status_wip
        self.assertRaises(StatusError, self.test_task3.resume)

    # PREV
    def test_resume_in_PREV_leaf_task(self):
        """testing if a StatusError will be raised when the resume action is
        used in a PREV leaf task
        """
        self.test_task3.status = self.status_prev
        self.assertRaises(StatusError, self.test_task3.resume)

    # HREV
    def test_resume_in_HREV_leaf_task(self):
        """testing if a StatusError will be raised when the resume action is
        used in a HREV leaf task
        """
        self.test_task3.status = self.status_hrev
        self.assertRaises(StatusError, self.test_task3.resume)

    # DREV
    def test_resume_in_DREV_leaf_task(self):
        """testing if a StatusError will be raised when the resume action is
        used in a DREV leaf task
        """
        self.test_task3.status = self.status_drev
        self.assertRaises(StatusError, self.test_task3.resume)

    # OH: no dependency -> WIP
    def test_resume_in_OH_leaf_task_with_no_dependencies(self):
        """testing if the status will be updated to WIP when the resume action
        is used in a OH leaf task with no dependencies
        """
        self.test_task3.status = self.status_oh
        self.test_task3.depends = []
        self.test_task3.resume()
        self.assertEqual(self.test_task3.status, self.status_wip)

    # OH: WIP dependencies -> DREV
    def test_resume_in_OH_leaf_task_with_WIP_dependencies(self):
        """testing if the status will be updated to DREV when the resume action
        is used in a OH leaf task with WIP dependencies
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_rts)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        # start working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + td(hours=1)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        # complete task3
        reviews = self.test_task3.request_review()
        for r in reviews:
            r.approve()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_rts)

        # start working on task9
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_wip)

        # hold task9
        self.test_task9.hold()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_oh)

        # request a revision to task3
        self.test_task3.request_revision(
            reviewer=self.test_user1
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_hrev)
        self.assertEqual(self.test_task9.status, self.status_oh)

        # now continue working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + td(hours=2),
            end=now + td(hours=3)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_oh)

        # now resume task9
        self.test_task9.resume()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_drev)

    # OH: HREV dependencies -> DREV
    def test_resume_in_OH_leaf_task_with_HREV_dependencies(self):
        """testing if the status will be updated to DREV when the resume action
        is used in a OH leaf task with HREV dependencies
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + td(hours=1)
        )

        reviews = self.test_task3.request_review()
        for r in reviews:
            r.approve()

        # task3 should be cmpl
        self.assertEqual(self.test_task3.status, self.status_cmpl)

        # start working on task9
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        # now continue working on test_task3
        self.test_task3.request_revision(
            reviewer=self.test_task3.resources[0]
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_hrev)
        self.assertEqual(self.test_task9.status, self.status_drev)

        # hold task9
        self.test_task9.hold()
        self.assertEqual(self.test_task9.status, self.status_oh)

        # resume task9
        self.test_task9.resume()
        self.assertEqual(self.test_task9.status, self.status_drev)

    # OH: PREV dependencies -> DREV
    def test_resume_in_OH_leaf_task_with_PREV_dependencies(self):
        """testing if the status will be updated to DREV when the resume action
        is used in a OH leaf task with PREV dependencies
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_rts)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        # start working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + td(hours=1)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        # complete task3
        reviews = self.test_task3.request_review()
        for r in reviews:
            r.approve()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_rts)

        # start working on task9
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_wip)

        # hold task9
        self.test_task9.hold()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_oh)

        # request a revision to task3
        self.test_task3.request_revision(
            reviewer=self.test_user1
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_hrev)
        self.assertEqual(self.test_task9.status, self.status_oh)

        # now continue working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + td(hours=2),
            end=now + td(hours=3)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_oh)

        # request a review for task3
        self.test_task3.request_review()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_prev)
        self.assertEqual(self.test_task9.status, self.status_oh)

        # now resume task9
        self.test_task9.resume()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_prev)
        self.assertEqual(self.test_task9.status, self.status_drev)

    # OH: DREV dependencies -> DREV
    def test_resume_in_OH_leaf_task_with_DREV_dependencies(self):
        """testing if the status will be updated to DREV when the resume action
        is used in a OH leaf task with DREV dependencies
        """
        self.test_task6.status = self.status_rts
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]
        self.test_task3.depends = [self.test_task6]

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_rts)
        self.assertEqual(self.test_task3.status, self.status_wfd)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()
        self.test_task6.create_time_log(
            resource=self.test_task6.resources[0],
            start=now,
            end=now + td(hours=1)
        )

        # approve task6
        reviews = self.test_task6.request_review()
        for r in reviews:
            r.approve()

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_cmpl)
        self.assertEqual(self.test_task3.status, self.status_rts)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        # start working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        # approve task3
        reviews = self.test_task3.request_review()
        for r in reviews:
            r.approve()

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_cmpl)
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_rts)

        # start working on task9
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now + td(hours=2),
            end=now + td(hours=3)
        )

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_cmpl)
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_wip)

        # hold task9
        self.test_task9.hold()

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_cmpl)
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_oh)

        # request a revision to task6
        self.test_task6.request_revision(
            reviewer=self.test_user1
        )

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_hrev)
        self.assertEqual(self.test_task3.status, self.status_drev)
        self.assertEqual(self.test_task9.status, self.status_oh)

        # resume task9
        self.test_task9.resume()

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_hrev)
        self.assertEqual(self.test_task3.status, self.status_drev)
        self.assertEqual(self.test_task9.status, self.status_drev)

    # OH: OH dependencies -> DREV
    def test_resume_in_OH_leaf_task_with_OH_dependencies(self):
        """testing if the status will be updated to WIP when the resume action
        is used in a OH leaf task with OH dependencies
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts

        # finish task3 first
        now = datetime.datetime.now()
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + datetime.timedelta(hours=1)
        )
        reviews = self.test_task3.request_review()
        for r in reviews:
            r.approve()

        self.test_task9.depends = [self.test_task3]

        # start working for task9
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now + datetime.timedelta(hours=1),
            end=now + datetime.timedelta(hours=2)
        )

        # now request a revision for task3
        self.test_task3.request_revision(reviewer=self.test_user1)
        self.assertEqual(self.test_task3.status, self.status_hrev)
        self.assertEqual(self.test_task9.status, self.status_drev)

        # enter a new time log for task3 to make it wip
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + datetime.timedelta(hours=3),
            end=now + datetime.timedelta(hours=4),
        )

        # and hold task3 and task9
        self.test_task9.hold()
        self.test_task3.hold()

        self.assertEqual(self.test_task3.status, self.status_oh)
        self.assertEqual(self.test_task9.status, self.status_oh)

        self.test_task9.resume()
        self.assertEqual(self.test_task9.status, self.status_drev)

    # OH: STOP dependencies -> WIP
    def test_resume_in_OH_leaf_task_with_STOP_dependencies(self):
        """testing if the status will be updated to WIP when the resume action
        is used in a OH leaf task with STOP dependencies
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        self.test_task3.status = self.status_stop
        self.test_task9.status = self.status_oh

        self.test_task9.resume()
        self.assertEqual(self.test_task9.status, self.status_wip)

    # OH: CMPL dependencies -> WIP
    def test_resume_in_OH_leaf_task_with_CMPL_dependencies(self):
        """testing if the status will be updated to WIP when the resume action
        is used in a OH leaf task with CMPL dependencies
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        self.test_task3.status = self.status_cmpl
        self.test_task9.status = self.status_oh

        self.test_task9.resume()
        self.assertEqual(self.test_task9.status, self.status_wip)

    # STOP: no dependency -> WIP
    def test_resume_in_STOP_leaf_task_with_no_dependencies(self):
        """testing if the status will be updated to WIP when the resume action
        is used in a STOP leaf task with no dependencies
        """
        self.test_task3.status = self.status_stop
        self.test_task3.depends = []
        self.test_task3.resume()
        self.assertEqual(self.test_task3.status, self.status_wip)

    # STOP: WIP dependencies -> DREV
    def test_resume_in_STOP_leaf_task_with_WIP_dependencies(self):
        """testing if the status will be updated to DREV when the resume action
        is used in a STOP leaf task with WIP dependencies
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_rts)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        # start working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + td(hours=1)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        # complete task3
        reviews = self.test_task3.request_review()
        for r in reviews:
            r.approve()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_rts)

        # start working on task9
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_wip)

        # stop task9
        self.test_task9.stop()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # request a revision to task3
        self.test_task3.request_revision(
            reviewer=self.test_user1
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_hrev)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # now continue working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + td(hours=2),
            end=now + td(hours=3)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # now resume task9
        self.test_task9.resume()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_drev)

    # STOP: HREV dependencies -> DREV
    def test_resume_in_STOP_leaf_task_with_HREV_dependencies(self):
        """testing if the status will be updated to DREV when the resume action
        is used in a STOP leaf task with HREV dependencies
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_rts)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        # start working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + td(hours=1)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        # complete task3
        reviews = self.test_task3.request_review()
        for r in reviews:
            r.approve()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_rts)

        # start working on task9
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_wip)

        # stop task9
        self.test_task9.stop()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # request a revision to task3
        self.test_task3.request_revision(
            reviewer=self.test_user1
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_hrev)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # now continue working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + td(hours=2),
            end=now + td(hours=3)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # request a review for task3
        reviews = self.test_task3.request_review()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_prev)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # request revisions
        for r in reviews:
            r.request_revision()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_hrev)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # now resume task9
        self.test_task9.resume()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_hrev)
        self.assertEqual(self.test_task9.status, self.status_drev)

    # STOP: PREV dependencies -> DREV
    def test_resume_in_STOP_leaf_task_with_PREV_dependencies(self):
        """testing if the status will be updated to DREV when the resume action
        is used in a STOP leaf task with PREV dependencies
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_rts)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        # start working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + td(hours=1)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        # complete task3
        reviews = self.test_task3.request_review()
        for r in reviews:
            r.approve()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_rts)

        # start working on task9
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_wip)

        # stop task9
        self.test_task9.stop()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # request a revision to task3
        self.test_task3.request_revision(
            reviewer=self.test_user1
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_hrev)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # now continue working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + td(hours=2),
            end=now + td(hours=3)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # request a review for task3
        self.test_task3.request_review()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_prev)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # now resume task9
        self.test_task9.resume()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_prev)
        self.assertEqual(self.test_task9.status, self.status_drev)

    # STOP: DREV dependencies -> DREV
    def test_resume_in_STOP_leaf_task_with_DREV_dependencies(self):
        """testing if the status will be updated to DREV when the resume action
        is used in a STOP leaf task with DREV dependencies
        """
        self.test_task6.status = self.status_rts
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]
        self.test_task3.depends = [self.test_task6]

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_rts)
        self.assertEqual(self.test_task3.status, self.status_wfd)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()
        self.test_task6.create_time_log(
            resource=self.test_task6.resources[0],
            start=now,
            end=now + td(hours=1)
        )

        # approve task6
        reviews = self.test_task6.request_review()
        for r in reviews:
            r.approve()

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_cmpl)
        self.assertEqual(self.test_task3.status, self.status_rts)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        # start working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        # approve task3
        reviews = self.test_task3.request_review()
        for r in reviews:
            r.approve()

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_cmpl)
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_rts)

        # start working on task9
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now + td(hours=2),
            end=now + td(hours=3)
        )

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_cmpl)
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_wip)

        # stop task9
        self.test_task9.stop()

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_cmpl)
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # request a revision to task6
        self.test_task6.request_revision(
            reviewer=self.test_user1
        )

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_hrev)
        self.assertEqual(self.test_task3.status, self.status_drev)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # resume task9
        self.test_task9.resume()

        # check statuses
        self.assertEqual(self.test_task6.status, self.status_hrev)
        self.assertEqual(self.test_task3.status, self.status_drev)
        self.assertEqual(self.test_task9.status, self.status_drev)

    # STOP: OH dependencies -> DREV
    def test_resume_in_STOP_leaf_task_with_OH_dependencies(self):
        """testing if the status will be updated to WIP when the resume action
        is used in a STOP leaf task with OH dependencies
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_rts)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        dt = datetime.datetime
        td = datetime.timedelta
        now = dt.now()

        # start working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + td(hours=1)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_wfd)

        # complete task3
        reviews = self.test_task3.request_review()
        for r in reviews:
            r.approve()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_rts)

        # start working on task9
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now + td(hours=1),
            end=now + td(hours=2)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_wip)

        # stop task9
        self.test_task9.stop()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # request a revision to task3
        self.test_task3.request_revision(
            reviewer=self.test_user1
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_hrev)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # now continue working on task3
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now + td(hours=2),
            end=now + td(hours=3)
        )

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_wip)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # hold task3
        self.test_task3.hold()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_oh)
        self.assertEqual(self.test_task9.status, self.status_stop)

        # now resume task9
        self.test_task9.resume()

        # check statuses
        self.assertEqual(self.test_task3.status, self.status_oh)
        self.assertEqual(self.test_task9.status, self.status_drev)

    # STOP: STOP dependencies -> WIP
    def test_resume_in_STOP_leaf_task_with_STOP_dependencies(self):
        """testing if the status will be updated to WIP when the resume action
        is used in a STOP leaf task with STOP dependencies
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        self.test_task3.status = self.status_stop
        self.test_task9.status = self.status_stop

        self.test_task9.resume()
        self.assertEqual(self.test_task9.status, self.status_wip)

    # STOP: CMPL dependencies -> WIP
    def test_resume_in_STOP_leaf_task_with_CMPL_dependencies(self):
        """testing if the status will be updated to WIP when the resume action
        is used in a STOP leaf task with CMPL dependencies
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        self.test_task3.status = self.status_cmpl
        self.test_task9.status = self.status_stop

        self.test_task9.resume()
        self.assertEqual(self.test_task9.status, self.status_wip)

    # CMPL
    def test_resume_in_CMPL_leaf_task(self):
        """testing if a StatusError will be raised when the resume action is used
        in a CMPL leaf task
        """
        self.test_task3.status = self.status_drev
        self.assertRaises(StatusError, self.test_task3.resume)

    # approve
    # WFD
    def test_approve_in_WFD_leaf_task(self):
        """testing if a StatusError will be raised when the approve action is
        used in a WFD leaf task
        """
        self.test_task3.status = self.status_wfd
        self.assertRaises(StatusError, self.test_task3.approve)

    # RTS
    def test_approve_in_RTS_leaf_task(self):
        """testing if a StatusError will be raised when the approve action is
        used in a RTS leaf task
        """
        self.test_task3.status = self.status_rts
        self.assertRaises(StatusError, self.test_task3.approve)

    # WIP
    def test_approve_in_WIP_leaf_task(self):
        """testing if a StatusError will be raised when the approve action is
        used in a WIP leaf task
        """
        self.test_task3.status = self.status_wip
        self.assertRaises(StatusError, self.test_task3.approve)

    # PREV: Status to CMPL
    def test_approve_in_PREV_leaf_task_status_changed_to_CMPL(self):
        """testing if the status will be set to CMPL when the approve action is
        used in a PREV leaf task
        """
        now = datetime.datetime.now()
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + datetime.timedelta(hours=1)
        )
        self.test_task3.request_review()
        self.test_task3.approve()
        self.assertEqual(self.test_task3.status, self.status_cmpl)

    # PREV: Dependent task status updates WFD -> RTS
    def test_approve_in_PREV_leaf_task_WFD_dependencies_are_updated_to_RTS(self):
        """testing if the WFD dependency statuses are updated to RTS when the
        approve action is used in a PREV leaf task
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        now = datetime.datetime.now()
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + datetime.timedelta(hours=1)
        )
        reviews = self.test_task3.request_review()
        self.assertEqual(self.test_task3.status, self.status_prev)

        self.test_task3.approve()
        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_rts)

    # PREV: Dependent task status updates DREV -> WIP
    def test_approve_in_PREV_leaf_task_DREV_dependencies_are_updated_to_WIP(self):
        """testing if the DREV dependency statuses are updated to WIP when the
        approve action is used in a PREV leaf task
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task9.depends = [self.test_task3]

        # hack the status (not good actually, makes this test a half test)
        self.test_task9.status = self.status_wip

        # create time logs first
        now = datetime.datetime.now()
        self.test_task3.create_time_log(
            resource=self.test_task3.resources[0],
            start=now,
            end=now + datetime.timedelta(hours=1)
        )
        reviews = self.test_task3.request_review()

        self.test_task3.approve()

        self.assertEqual(self.test_task3.status, self.status_cmpl)
        self.assertEqual(self.test_task9.status, self.status_wip)

    # PREV: Dependent task status updates other dependencies stay intact
    def test_approve_in_PREV_leaf_task_other_dependency_statuses_are_intact(self):
        """testing if the other dependency statuses will stay intact when the
        approve action is used in a PREV leaf task
        """
        self.test_task3.status = self.status_rts
        self.test_task9.status = self.status_rts
        self.test_task5.depends = [self.test_task3]
        self.test_task6.depends = [self.test_task3]
        self.test_task8.depends = [self.test_task3]

        self.test_task3.status = self.status_prev
        self.test_task5.status = self.status_oh
        self.test_task6.status = self.status_stop
        self.test_task8.status = self.status_prev

        self.test_task3.approve()
        self.assertEqual(self.test_task5.status, self.status_oh)
        self.assertEqual(self.test_task6.status, self.status_stop)
        self.assertEqual(self.test_task8.status, self.status_prev)

    # PREV: Parent task status updated
    def test_approve_in_PREV_leaf_task_parent_status_updated_correctly(self):
        """testing if the parent task status is updated correctly when the
        approve action is used in a PREV leaf task
        """
        self.test_task9.depends = []

        self.test_task9.status = self.status_rts
        self.test_task1.status = self.status_wip
        self.test_task7.status = self.status_wip
        self.test_task8.status = self.status_wip
        self.test_task2.status = self.status_wip

        now = datetime.datetime.now()
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now,
            end=now + datetime.timedelta(hours=1)
        )

        reviews = self.test_task9.request_review()
        self.assertEqual(self.test_task9.status, self.status_prev)

        self.test_task9.approve()
        self.assertEqual(self.test_task9.status, self.status_cmpl)
        self.assertEqual(self.test_asset1.status, self.status_cmpl)
        self.assertEqual(self.test_task7.status, self.status_cmpl)
        self.assertEqual(self.test_task2.status, self.status_wip)

    # PREV: Parents of dependent task statuses are updated
    def test_approve_in_PREV_leaf_task_parents_of_dependent_task_statuses_updated_correctly(self):
        """testing if the parents of dependent task statuses are updated
        correctly when the approve action is used in a PREV leaf task
        """
        self.test_task9.depends = []
        self.test_task6.depends = [self.test_task9]

        self.test_task9.status = self.status_wip
        self.test_asset1.status = self.status_wip
        self.test_task7.status = self.status_wip
        self.test_task8.status = self.status_wip
        self.test_task2.status = self.status_wip

        self.test_task4.status = self.status_wfd
        self.test_task5.status = self.status_wfd
        self.test_task6.status = self.status_wfd
        self.test_asset1.status = self.status_wfd

        now = datetime.datetime.now()
        self.test_task9.create_time_log(
            resource=self.test_task9.resources[0],
            start=now,
            end=now + datetime.timedelta(hours=1)
        )
        reviews = self.test_task9.request_review()
        self.assertEqual(self.test_task9.status, self.status_prev)

        self.test_task9.approve()
        self.assertEqual(self.test_task9.status, self.status_cmpl)
        self.assertEqual(self.test_asset1.status, self.status_cmpl)
        self.assertEqual(self.test_task7.status, self.status_cmpl)
        self.assertEqual(self.test_task2.status, self.status_wip)

        self.assertEqual(self.test_task4.status, self.status_wfd)
        self.assertEqual(self.test_task5.status, self.status_wfd)
        self.assertEqual(self.test_task6.status, self.status_rts)
        self.assertEqual(self.test_task1.status, self.status_rts)

    #PREV: 
    def test_approve_in_PREV_leaf_task_review_instance_statuses_updated_correctly(self):
        """testing if the Review instances values are correctly updated to APP
        when the approve action is used in a PREV leaf task
        """
        self.test_task3.status = self.status_wip

        # create reviews automatically
        reviews = self.test_task3.request_review()

        # check the statuses
        self.assertEqual(reviews[0].status.code, 'NEW')
        self.assertEqual(reviews[1].status.code, 'NEW')

        # approve all of them
        self.test_task3.approve()

        # now expect the statuses of the reviews to be all app
        self.assertEqual(reviews[0].status.code, 'APP')
        self.assertEqual(reviews[1].status.code, 'APP')

    # HREV
    def test_approve_in_HREV_leaf_task(self):
        """testing if a StatusError will be raised when the approve action is
        used in a HREV leaf task
        """
        self.test_task9.status = self.status_hrev
        self.assertRaises(StatusError, self.test_task9.approve)

    # DREV
    def test_approve_in_DREV_leaf_task(self):
        """testing if a StatusError will be raised when the approve action is
        used in a DREV leaf task
        """
        self.test_task9.status = self.status_drev
        self.assertRaises(StatusError, self.test_task9.approve)

    # OH
    def test_approve_in_OH_leaf_task(self):
        """testing if a StatusError will be raised when the approve action is
        used in a OH leaf task
        """
        self.test_task9.status = self.status_oh
        self.assertRaises(StatusError, self.test_task9.approve)

    # STOP
    def test_approve_in_STOP_leaf_task(self):
        """testing if a StatusError will be raised when the approve action is
        used in a STOP leaf task
        """
        self.test_task9.status = self.status_stop
        self.assertRaises(StatusError, self.test_task9.approve)

    # CMPL
    def test_approve_in_CMPL_leaf_task(self):
        """testing if a StatusError will be raised when the approve action is
        used in a CMPL leaf task
        """
        self.test_task9.status = self.status_cmpl
        self.assertRaises(StatusError, self.test_task9.approve)
