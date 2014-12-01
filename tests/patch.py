import porc
import unittest
import random, string


class PatchTest(unittest.TestCase):

    def setUp(self):
        self.patch = porc.Patch()

    def test_add(self):
        expected = list()
        for i in range(10):
            levels = random.randint(1,3)
            path = random_path(levels)
            length = random.randint(4,20)
            value = randomword(length)
            self.patch.add(path, value)
            operation = {
                'op': 'add',
                'path': path,
                'value': value
            }
            expected.append(operation)

        assert self.patch.operations == expected

    def test_remove(self):
        expected = list()
        for i in range(10):
            levels = random.randint(1,3)
            path = random_path(levels)
            self.patch.remove(path)
            operation = {
                'op': 'remove',
                'path': path
            }
            expected.append(operation)

        assert self.patch.operations == expected

    def test_replace(self):
        expected = list()
        for i in range(10):
            levels = random.randint(1,3)
            path = random_path(levels)
            length = random.randint(4,20)
            value = randomword(length)
            self.patch.replace(path, value)
            operation = {
                'op': 'replace',
                'path': path,
                'value': value
            }
            expected.append(operation)

        assert self.patch.operations == expected

    def test_move(self):
        expected = list()
        for i in range(10):
            new_path = random_path(random.randint(1,3))
            old_path = random_path(random.randint(1,3))
            self.patch.move(old_path, new_path)
            operation = {
                'op': 'move',
                'path': new_path,
                'from': old_path
            }
            expected.append(operation)

        assert self.patch.operations == expected

    def test_copy(self):
        expected = list()
        for i in range(10):
            copy = random_path(random.randint(1,3))
            original = random_path(random.randint(1,3))
            self.patch.copy(original, copy)
            operation = {
                'op': 'copy',
                'path': copy,
                'from': original
            }
            expected.append(operation)

        assert self.patch.operations == expected

    def test_test(self):
        expected = list()
        for i in range(10):
            levels = random.randint(1,3)
            path = random_path(levels)
            length = random.randint(4,20)
            value = randomword(length)
            self.patch.test(path, value)
            operation = {
                'op': 'test',
                'path': path,
                'value': value
            }
            expected.append(operation)

        assert self.patch.operations == expected

    def test_increment(self):
        expected = list()
        for i in range(10):
            # Test default value
            levels = random.randint(1,3)
            path = random_path(levels)
            self.patch.increment(path)
            operation = {
                'op': 'inc',
                'path': path,
                'value': 1
            }
            expected.append(operation)
            # Test value param
            levels = random.randint(1,3)
            path = random_path(levels)
            value = random.randint(1,10)
            self.patch.increment(path, value)
            operation = {
                'op': 'inc',
                'path': path,
                'value': value,
            }
            expected.append(operation)

        assert self.patch.operations == expected

    def test_decrement(self):
        expected = list()
        for i in range(10):
            # Test default value
            levels = random.randint(1,3)
            path = random_path(levels)
            self.patch.decrement(path)
            operation = {
                'op': 'inc',
                'path': path,
                'value': -1
            }
            expected.append(operation)
            # Test value param
            levels = random.randint(1,3)
            path = random_path(levels)
            value = random.randint(1,10)
            self.patch.decrement(path, value)
            operation = {
                'op': 'inc',
                'path': path,
                'value': value*-1,
            }
            expected.append(operation)

        assert self.patch.operations == expected

    def test_chaining(self):
        levels = random.randint(1,3)
        path = random_path(levels)
        from_path = random_path(random.randint(1,3))
        length = random.randint(4,20)
        value = randomword(length)
        inc_value = random.randint(1,10)
        self.patch.add(path, value).remove(path).replace(path, value).move(from_path, path).copy(from_path, path).test(path, value).increment(path).increment(path, inc_value).decrement(path).decrement(path, inc_value)
        expected =[
            {'op': 'add', 'path': path, 'value': value},
            {'op': 'remove', 'path': path},
            {'op': 'replace', 'path': path, 'value': value},
            {'op': 'move', 'path': path, 'from': from_path},
            {'op': 'copy', 'path': path, 'from': from_path},
            {'op': 'test', 'path': path, 'value': value},
            {'op': 'inc', 'path': path, 'value': 1},
            {'op': 'inc', 'path': path, 'value': inc_value},
            {'op': 'inc', 'path': path, 'value': -1},
            {'op': 'inc', 'path': path, 'value': inc_value*-1}
        ]

        assert self.patch.operations == expected

def random_path(levels=1, token='.'):
    path = list()
    for level in range(levels):
        path.append(randomword(8))
    return token.join(path)

def randomword(length, source=string.ascii_lowercase):
   return ''.join(random.choice(source) for i in range(length))
