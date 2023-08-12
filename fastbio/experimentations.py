import openai
import json
from typing import Tuple , List,Optional
from pydantic import BaseModel
openai.api_key = "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"

class Output(BaseModel):

	title : str 
	abstract : str
	author : List[str]


class LLMParser:

	def create_prompt(self,instr:str,query:str,examples:List[str],topK:Optional[int] = 3) -> str:
		beforeEx = f"Instruction : {instr}\n" 
		beforeFiller = "Here are some examples to understand the instruction better\n"
		Ex = ""
		for i in range(topK):
			Ex += f"Example{i} : \n {examples[i]} \n"
		afterFiller = "Now for the query given here generate the output that is in accordance with the above examples. Just write the output , nothing else. Only use the information in the query . Dont make anything up.\n"
		end = f"Input : \n {query} \n Output : \n"
		finalPrompt = beforeEx + beforeFiller + Ex + afterFiller + end
		return finalPrompt


	def load(self,data):
		instr , query , examples , topK = data[0] , data[1] , data[2] , data[3]
		currPrompt = self.create_prompt(instr,query,examples,topK)
		response = openai.Completion.create(model="",prompt=currPrompt,temperature=0)
		response = response["choices"][0]["text"]
		return response
		jsonResponse = json.loads(response)

		try:
			Output(**jsonResponse)
			return jsonResponse
		except Exception as e:
			print("Formatting Error!")
			return None

		#validate 



if __name__ == "__main__":
	instruction = "Extract the Title and Abstract of a Publication from the given text input. The output should be a json with keys Title and Abstract.\n"
	query_pre = "Query : \n"
	examples = []

	with open("example1.txt") as file:
		example = file.read()
	examples.append(example)

	# with open("example2.txt") as file:
	# 	example = file.read()
	# examples.append(example)

	query = f"""15921050 2005 08 01 2019 11 09 1464-7931 80 2 2005 May Biological reviews of the Cambridge Philosophical Society Biol Rev Camb Philos Soc Why repetitive DNA is essential to genome function. 227 250 227-50 There are clear theoretical reasons and many well-documented examples which show that repetitive, DNA is essential for genome function. Generic repeated signals in the DNA are necessary to format expression of unique coding sequence files and to organise additional functions essential for genome replication and accurate transmission to progeny cells. Repetitive DNA sequence elements are also fundamental to the cooperative molecular interactions forming nucleoprotein complexes. Here, we review the surprising abundance of repetitive DNA in many genomes, describe its structural diversity, and discuss dozens of cases where the functional importance of repetitive elements has been studied in molecular detail. In particular, the fact that repeat elements serve either as initiators or boundaries for heterochromatin domains and provide a significant fraction of scaffolding/matrix attachment regions (S/MARs) suggests that the repetitive component of the genome plays a major architectonic role in higher order physical structuring. Employing an information science model, the 'functionalist' perspective on repetitive DNA leads to new ways of thinking about the systemic organisation of cellular genomes and provides several novel possibilities involving repeat elements in evolutionarily significant genome reorganisation. These ideas may facilitate the interpretation of comparisons between sequenced genomes, where the repetitive DNA component is often greater than the coding sequence component. Shapiro James A JA Department of Biochemistry and Molecular Biology, University of Chicago, 920 E. 58th Street, Chicago, IL 60637, USA. jsha@uchicago.edu von Sternberg Richard R eng Journal Article Review England Biol Rev Camb Philos Soc 0414576 0006-3231 0 DNA Transposable Elements 9007-49-2 DNA IM Animals DNA analysis genetics DNA Transposable Elements Gene Expression Regulation Genome Repetitive Sequences, Nucleic Acid Species Specificity 247 2005 6 1 9 0 2005 8 2 9 0 2005 6 1 9 0 ppublish 15921050 10.1017/s1464793104006657 """
	obj = LLMParser()
	response = obj.load([instruction,query,examples,1])
	print(response)
	# reqKeys = set(["Title","Abstract"])
	# outputKeys = set(obj.keys)
	# if reqKeys != outputKeys:
	# 	print("Output is wrong")











