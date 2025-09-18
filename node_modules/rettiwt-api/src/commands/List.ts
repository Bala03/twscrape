import { Command, createCommand } from 'commander';

import { output } from '../helper/CliUtils';
import { Rettiwt } from '../Rettiwt';

/**
 * Creates a new 'list' command which uses the given Rettiwt instance.
 *
 * @param rettiwt - The Rettiwt instance to use.
 * @returns The created 'list' command.
 */
function createListCommand(rettiwt: Rettiwt): Command {
	// Creating the 'list' command
	const list = createCommand('list').description('Access resources releated to lists');

	// Members
	list.command('members')
		.description('Fetch the list of members of the given tweet list')
		.argument('<id>', 'The id of the tweet list')
		.argument('[count]', 'The number of members to fetch')
		.argument('[cursor]', 'The cursor to the batch of members to fetch')
		.action(async (id: string, count?: string, cursor?: string) => {
			try {
				const members = await rettiwt.list.members(id, count ? parseInt(count) : undefined, cursor);
				output(members);
			} catch (error) {
				output(error);
			}
		});

	// Tweets
	list.command('tweets')
		.description('Fetch the list of tweets in the tweet list with the given id')
		.argument('<id>', 'The id of the tweet list')
		.argument('[count]', 'The number of tweets to fetch')
		.argument('[cursor]', 'The cursor to the batch of tweets to fetch')
		.action(async (id: string, count?: string, cursor?: string) => {
			try {
				const tweets = await rettiwt.list.tweets(id, count ? parseInt(count) : undefined, cursor);
				output(tweets);
			} catch (error) {
				output(error);
			}
		});

	return list;
}

export default createListCommand;
