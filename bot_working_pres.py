from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
import pickle as pkl
import numpy as np
from explanation_generation import sample_definition
from predictions_v2 import guesser


class ContactGame:
    def __init__(self, bot_role, dict_dim):
        self.Answers = []
        self.Explanations = None
        self.updater = Updater("855197924:AAHkIDeoWI_nypSi7SBTjXy8YJMP2OSRv5Y", use_context=True)

        self.chat_id = None
        self.group_id = None

        self.time_to_answer = 10

        self.bot_role = bot_role
        self.host_id = None
        self.users_id = []
        self.explainer_id = None

        self.words = None
        self.N = dict_dim
        self.word_to_expl = None
        self.cur_sequence = None

        self.contact_sustain = False
        self.contact_fail = False

    def join(self, update, context):
        self.users_id.append(update.message.from_user.id)
        print(self.users_id)
        update.message.reply_text('{}, you joined the game'.format(update.message.from_user.first_name))

    def start(self, update, context):
        self.Answers = []
        self.Explanations = None
        with open("words_{}.pkl".format(self.N), "rb") as f:
            self.words = pkl.load(f)
            self.words = np.array(self.words)
        self.chat_id = update.message.chat.id
        context.bot.send_message(self.chat_id, text='Hello! You started the game!')

        self.users_id = np.array(self.users_id)

        if self.bot_role == 'player':
            self.host_id = int(np.random.choice(self.users_id))
            users = self.users_id.copy()
            users = np.array(users)
            users = np.delete(users, np.where(users == self.host_id))
            users = np.append(users, 0)
            self.explainer_id = int(np.random.choice(users))
        else:
            self.explainer_id = int(np.random.choice(self.users_id))
            self.host_id = 0

        self.word_to_expl = np.random.choice(self.words)
        self.cur_sequence = self.word_to_expl[:1]

        sample_word = np.random.choice([word for word in self.words if word.startswith(self.cur_sequence)])
        context.bot.send_message(self.chat_id, text='Known letters: {}'.format(self.cur_sequence))
        print('expl_id', self.explainer_id, 'host_id', self.host_id)
        if self.host_id != 0:
            context.bot.send_message(self.host_id, text='Your word is "{}"'.format(self.word_to_expl))
            context.bot.send_message(self.chat_id, text='{} is the host!'.format(context.bot.getChatMember(self.chat_id, self.host_id).user.first_name))
        if self.explainer_id != 0:
            context.bot.send_message(self.explainer_id, text='You need explain the word "{}"'.format(sample_word))
            context.bot.send_message(self.chat_id, text='{} is going to explain a word!'.format(context.bot.getChatMember(self.chat_id, self.explainer_id).user.first_name))
            self.Answers.append([self.explainer_id, sample_word])
        else:
            available_words = [word for word in self.words if word.startswith(self.cur_sequence)]
            word = np.random.choice(available_words)
            print(word)
            context.bot.send_message(self.chat_id, text=sample_definition(word))
            self.Answers.append([self.explainer_id, word])

    def update_sequence(self):
        self.cur_sequence = self.word_to_expl[:len(self.cur_sequence)+1]

    def update_roles(self):
        if self.bot_role == 'player':
            users = self.users_id.copy()
            users = np.array(users)
            users = np.delete(users, np.where(users == self.host_id))
            users = np.append(users, 0)
            print(users)
            self.explainer_id = int(np.random.choice(users))
        else:
            self.explainer_id = int(np.random.choice(self.users_id))
        print('expl_id', self.explainer_id, 'host_id', self.host_id)

    def echo(self, update, context):
        if update.message.chat.type == 'group':
            if 'contact_job' not in context.chat_data:
                # context.bot.send_message(self.chat_id, text='group chat')
                if update.message.from_user.id == self.explainer_id:
                    self.Explanations = [update.message.from_user.id, update.message.text]

                    if self.bot_role == 'player' and self.explainer_id != 0:
                        cur_words_global_list = set(list(self.words))
                        p, word_list = guesser.predict_closest_distrn(self.Explanations[1])
                        p = np.array([p[i] for i, word in enumerate(word_list) if
                                      word.startswith(self.cur_sequence) and word in cur_words_global_list])
                        word_list = np.array([word for word in word_list if
                                              word.startswith(self.cur_sequence) and word in cur_words_global_list])

                        p /= (p.sum() + 1e-10)
                        prediction = word_list[np.argmax(p)]
                        prediction_word, frec = prediction, p[np.argmax(p)]
                        print(frec, prediction_word)
                        if frec > 0.15:
                            self.Answers.append([0, prediction_word])
                            job = context.job_queue.run_once(self.check_contact, self.time_to_answer+5,
                                                             context=(self.chat_id, context))
                            context.chat_data['contact_job'] = job
                            self.contact_sustain = False
                            self.contact_fail = False
                            context.bot.send_message(self.chat_id, text='I am {} percent sure that I know what you mean! I am starting the Contact!'.format(int(frec*100)))
                        else:
                            context.bot.send_message(self.chat_id, text='I\'m not sure about this word')
        elif update.message.chat.type == 'private':
            if update.message.from_user.id != self.explainer_id:
                self.Answers.append([update.message.from_user.id, update.message.text])

    def check_contact(self, context):
        """Check 'Contact' state"""
        chat_id, context = context.job.context

        self.Answers = np.array(self.Answers)
        # context.bot.send_message(self.chat_id, text=self.Answers)
        _, pos = np.unique(self.Answers[:, 1], return_index=True, axis=0)
        # print(_, pos)
        answers = [ans for ans in self.Answers[:, 1] if ans.startswith(self.cur_sequence)]
        print(answers, self.Answers[pos, 1])
        if self.contact_fail:
            return
        elif len(set(answers)) == 1 and len(answers) >= 2:
            context.bot.send_message(chat_id, text='Successful contact!')
            self.update_sequence()
            self.update_roles()
            self.contact_sustain = True
            context.bot.send_message(chat_id, text='Known letters: {}'.format(self.cur_sequence))
            if len(self.cur_sequence) == len(self.word_to_expl):
                context.bot.send_message(chat_id, text='Yay, you got it! You win!')
        else:
            print(self.Answers)
            for j in range(self.Answers.shape[0]):

                self.Answers[j, 0] = "Bot: " if self.Answers[j, 0] == '0' else context.bot.getChatMember(self.chat_id, self.Answers[j, 0]).user.first_name


            context.bot.send_message(chat_id, text='Unsuccessful contact: players did not submit matching words. {}'.format(self.Answers))
            self.contact_sustain = True
            self.contact_fail = True
            self.update_roles()

        if self.bot_role == 'host' and not self.contact_fail:
            context.bot.send_message(chat_id,
                                     text='Oh, No! You tricked me, I could not guess your word. I\'ll give you the next letter.')
            context.bot.send_message(chat_id, text='Known letters: {}'.format(self.cur_sequence))

        self.Answers = []
        self.Explanations = None
        job = context.chat_data['contact_job']
        job.schedule_removal()
        del context.chat_data['contact_job']

        available_words = [word for word in self.words if word.startswith(self.cur_sequence)]
        if self.explainer_id != 0:
            sample_word = np.random.choice(available_words)
            context.bot.send_message(self.explainer_id, text='You need explain the word "{}"'.format(sample_word))
            context.bot.send_message(self.chat_id, text='{} is going to explain a word! I\'ve sent him or her a message.'.format(context.bot.getChatMember(self.chat_id, self.explainer_id).user.first_name))
            self.Answers.append([self.explainer_id, sample_word])
        elif self.explainer_id == 0:
            if not available_words:
                context.bot.send_message(self.chat_id, text='I could not find any words matching the sequence!')
                return
            else:
                word = np.random.choice(available_words)
                print(word)
                try:
                    context.bot.send_message(self.chat_id, text=sample_definition(word))
                    self.Answers.append([self.explainer_id, word])
                except KeyError:
                    self.update_roles()
                    self.Answers = []
                    available_words = [word for word in self.words if word.startswith(self.cur_sequence)]
                    if self.explainer_id != 0:
                        sample_word = np.random.choice(available_words)
                        context.bot.send_message(self.explainer_id,
                                                 text='You need explain the word "{}"'.format(sample_word))
                        context.bot.send_message(self.chat_id, text='{} is going to explain a word!'.format(
                            context.bot.getChatMember(self.chat_id, self.explainer_id).user.first_name))
                        self.Answers.append([self.explainer_id, sample_word])
                    elif self.explainer_id == 0:
                        if not available_words:
                            context.bot.send_message(self.chat_id, text='I could not find any words matching the sequence!')
                            return
                        else:
                            word = np.random.choice(available_words)
                            print(word)
                            context.bot.send_message(self.chat_id, text=sample_definition(word))
                            self.Answers.append([self.explainer_id, word])

    def prediction_word(self, _context):
        chat_id, context = _context.job.context
        if self.contact_sustain:
            job = context.chat_data['prediction_job']
            job.schedule_removal()
            del context.chat_data['prediction_job']
            return

        cur_words_global_list = set(list(self.words))
        p, word_list = guesser.predict_closest_distrn(self.Explanations[1])
        p = np.array([p[i] for i, word in enumerate(word_list) if
                      word.startswith(self.cur_sequence) and word in cur_words_global_list])
        word_list = np.array([word for word in word_list if word.startswith(self.cur_sequence) and word in cur_words_global_list])


        if not word_list.shape[0]:
            print("No matching words left")
        prediction = word_list[np.argmax(p)]

        if not prediction:
            context.bot.send_message(chat_id, text='Doesnt\'t find any words! The host wins :(')
            return
        else:
            self.words = np.delete(self.words, np.where(self.words == prediction))
        context.bot.send_message(chat_id, text='I think you explained {}!'.format(prediction))

        if prediction == self.word_to_expl:
            self.contact_fail = True
            job = context.chat_data['prediction_job']
            job.schedule_removal()
            del context.chat_data['prediction_job']
            if 'contact_job' not in context.chat_data:
                print('You have no active Contact, but prediction word -- {}'.format(prediction))
                return

            job = context.chat_data['contact_job']
            job.schedule_removal()
            del context.chat_data['contact_job']

            context.bot.send_message(chat_id, text='Haha, I got your word!')
            return

        else:
            time_when_predict = np.random.randint(self.time_to_answer//2, self.time_to_answer)
            job = context.job_queue.run_once(self.prediction_word, time_when_predict, context=(chat_id, context))
            context.chat_data['prediction_job'] = job

    def set_contact(self, update, context):
        """Add a job to the queue."""
        chat_id = update.message.chat_id
        try:
            # Add job to queue
            job = context.job_queue.run_once(self.check_contact, self.time_to_answer, context=(chat_id, context))
            context.chat_data['contact_job'] = job
            self.contact_sustain = False
            self.contact_fail = False

            if self.bot_role == 'host':
                time_when_predict = np.random.randint(self.time_to_answer//3, self.time_to_answer)
                job = context.job_queue.run_once(self.prediction_word, time_when_predict, context=(chat_id, context))
                context.chat_data['prediction_job'] = job

        except (IndexError, ValueError):
            update.message.reply_text('Usage: /contact')

    @staticmethod
    def unset_contact(update, context):
        """Remove the job if the user changed their mind."""
        if 'contact_job' not in context.chat_data:
            update.message.reply_text('You have no active timer')
            return

        job = context.chat_data['job']
        job.schedule_removal()
        del context.chat_data['job']

        update.message.reply_text('Timer successfully unset!')

    def set_sequence(self, update, context):
        """Add a job to the queue."""
        try:
            # args[0] should contain the time for the timer in seconds
            sequence = context.args[0]
            if type(sequence) == 'str':
                update.message.reply_text('Sorry type a string sequence!')
                return

            # Add job to queue
            self.cur_sequence = sequence

            update.message.reply_text('Sequence successfully set!')

        except (IndexError, ValueError):
            update.message.reply_text('Usage: /seq <sequence>')

    def give_up(self, update, context):
        context.bot.send_message(self.chat_id, text='The word is -- {}'.format(self.word_to_expl))

    def skip(self, update, context):
        self.update_roles()
        self.Answers = []
        print(self.explainer_id)
        available_words = [word for word in self.words if word.startswith(self.cur_sequence)]
        if self.explainer_id != 0:
            sample_word = np.random.choice(available_words)
            context.bot.send_message(self.explainer_id, text='You need explain this word -- {}'.format(sample_word))
            context.bot.send_message(self.chat_id, text='{} is going to explain a word'.format(
                context.bot.getChatMember(self.chat_id, self.explainer_id).user.first_name))
            self.Answers.append([self.explainer_id, sample_word])
        elif self.explainer_id == 0:
            if not available_words:
                context.bot.send_message(self.chat_id, text='Doesnt\'t find any words!')
                return
            else:
                word = np.random.choice(available_words)
                print(word)
                context.bot.send_message(self.chat_id, text=sample_definition(word))
                self.Answers.append([self.explainer_id, word])

    def run(self):
        # Get the dispatcher to register handlers
        dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("startgame", self.start,
                                      pass_args=True,
                                      pass_chat_data=True))
        dp.add_handler(CommandHandler("join", self.join,
                                      pass_args=True,
                                      pass_chat_data=True))
        dp.add_handler(CommandHandler("help", self.start))
        dp.add_handler(CommandHandler("contact", self.set_contact,
                                      pass_args=True,
                                      pass_job_queue=True,
                                      pass_chat_data=True))
        dp.add_handler((MessageHandler(Filters.text, self.echo)))
        dp.add_handler(CommandHandler("check", self.check_contact,
                                      pass_args=True,
                                      pass_job_queue=True,
                                      pass_chat_data=True))
        dp.add_handler(CommandHandler("seq", self.set_sequence,
                                      pass_args=True,
                                      pass_job_queue=True,
                                      pass_chat_data=True))
        dp.add_handler(CommandHandler("give_up", self.give_up,
                                      pass_args=True,
                                      pass_job_queue=True,
                                      pass_chat_data=True))
        dp.add_handler(CommandHandler("skip", self.skip,
                                      pass_args=True,
                                      pass_job_queue=True,
                                      pass_chat_data=True))

        while True:
            # Start the Bot
            self.updater.start_polling()

            # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
            # SIGABRT. This should be used most of the time, since start_polling() is
            # non-blocking and will stop the bot gracefully.
            self.updater.idle()


if __name__ == '__main__':
    game = ContactGame(bot_role='player', dict_dim=3000)
    game.run()
