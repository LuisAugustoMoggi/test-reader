from test_reader.discover.matchers.matcher import Matcher
from test_reader.discover.matchers.matcher_result import MatcherResult
from test_reader.config.configurationtest import ConfigurationTest
import re

from test_reader.discover.matchers.matcher_result_type import MatcherResultType


class TestMatcher(Matcher):

    def matches(self, file_path: str) -> [MatcherResult]:
        types_by_test_name = {}
        for test_type in self.test_config.get_type_names():
            found_tests = self.__get_tests_by_type(file_path, test_type)
            self.__append_tests_to_dict(found_tests, test_type, types_by_test_name)

        return self.__build_results(types_by_test_name)

    @staticmethod
    def __append_tests_to_dict(found_tests, test_type, types_by_test_name):
        for test_name in found_tests:
            if test_name not in types_by_test_name.keys():
                types_by_test_name[test_name] = []
            types_by_test_name[test_name].append(test_type)

    def __get_tests_by_type(self, file_path, test_type) -> [str]:
        curr_test_config = self.test_config.get_type_by_name(test_type)

        found_tests = {}

        if curr_test_config.test_rules.test_description_strategy == 'SAME_LINE':
            found_tests = self.__get_tests_by_same_line_strategy(curr_test_config, file_path)
        elif curr_test_config.test_rules.test_description_strategy == 'NEXT_LINE':
            found_tests = self.__get_tests_by_next_line_strategy(curr_test_config, file_path)
        elif curr_test_config.test_rules.test_description_strategy == 'MULTIPLE_LINE':
            found_tests = self.__get_tests_by_multiple_line_strategy(curr_test_config, file_path)

        return found_tests

    def __get_tests_by_next_line_strategy(self, curr_test_config, file_path) -> [str]:
        has_test = False
        found_tests = []
        exclude_test = False

        with open(file_path) as file:
            for line in file:
                if curr_test_config.test_rules.test_description_strategy == 'NEXT_LINE' and has_test and line.strip() != '':
                    found_tests.append(self.__get_test_description(curr_test_config, line.strip()))
                    has_test = False
                    continue

                if re.match(curr_test_config.test_rules.test_notation, line.strip()):
                    if not exclude_test:
                        has_test = True
                    else:
                        exclude_test = False
                    continue

                exclude_test = self.__should_exclude_test(curr_test_config, line.strip())

                if self.__should_exclude_test_next_line(curr_test_config, line.strip()):
                    found_tests.remove(found_tests.__getitem__(found_tests.__len__() - 1))

        return found_tests

    def __should_exclude_test(self, curr_test_config, line):
        exclude_test = False
        if curr_test_config.test_rules.test_exclusion_regex and \
                curr_test_config.test_rules.test_exclusion_strategy == 'BEFORE_LINE':
            if re.match(curr_test_config.test_rules.test_exclusion_regex, line.strip()):
                exclude_test = True
        return exclude_test

    def __should_exclude_test_next_line(self, curr_test_config, line):
        exclude_test = False
        if curr_test_config.test_rules.test_exclusion_regex and \
                curr_test_config.test_rules.test_exclusion_strategy == 'NEXT_LINE':
            if re.match(curr_test_config.test_rules.test_exclusion_regex, line.strip()):
                exclude_test = True
        return exclude_test

    def __get_tests_by_same_line_strategy(self, curr_test_config: ConfigurationTest, file_path) -> [str]:
        found_tests = []
        exclude_test = False

        with open(file_path) as file:
            for line in file:
                if re.match(curr_test_config.test_rules.test_notation, line.strip()):
                    if not exclude_test:
                        found_tests.append(self.__get_test_description(curr_test_config, line))
                    else:
                        exclude_test = False
                        continue

                exclude_test = self.__should_exclude_test(curr_test_config, line.strip())

                if self.__should_exclude_test_next_line(curr_test_config, line.strip()):
                    found_tests.remove(found_tests.__getitem__(found_tests.__len__() - 1))

        return found_tests

    def __get_tests_by_multiple_line_strategy(self, curr_test_config: ConfigurationTest, file_path) -> [str]:
        found_tests = []
        exclude_test = False

        file_content = ''
        with open(file_path) as file:
            lines = file.readlines()
            for line in lines:
                file_content += line

        with open(file_path) as file:
            for line in file:
                if re.match(curr_test_config.test_rules.test_notation, line.strip()):
                    if not exclude_test:
                        found_tests.append(self.__get_test_multiline_description(curr_test_config, line, file_content))
                    else:
                        exclude_test = False
                        continue

                exclude_test = self.__should_exclude_test(curr_test_config, line.strip())

                if self.__should_exclude_test_next_line(curr_test_config, line.strip()):
                    found_tests.remove(found_tests.__getitem__(found_tests.__len__() - 1))

            return found_tests

    @staticmethod
    def __get_test_description(curr_test_config, line):
        result = re.search(curr_test_config.test_rules.test_description_regex, line.strip())
        if result:
            position = result.groups().__len__()
            return result.group(position).strip()
        else:
            return line.strip()

    @staticmethod
    def __get_test_multiline_description(curr_test_config, line, file_content):
        result = re.search(curr_test_config.test_rules.test_description_regex, line.strip())
        if result:
            position = result.groups().__len__()
            initial_description = result.group(position).strip()
            initial_regex = initial_description.replace("(", "\\(")

            multiline_search_regex = initial_regex + curr_test_config.test_rules.test_description_multiline_regex
            multiline_result = re.search(multiline_search_regex, file_content, re.MULTILINE)
            if multiline_result:
                multiline_position = multiline_result.groups().__len__()
                return initial_description + multiline_result.group(multiline_position)
            else:
                return initial_description
        else:
            return line.strip()

    @staticmethod
    def __build_results(types_by_test_name) -> [MatcherResult]:
        results = []
        for test_name in types_by_test_name.keys():
            results.append(MatcherResult(test_name, types_by_test_name[test_name], MatcherResultType.test))

        return results
